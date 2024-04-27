# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-27 21:26:58
     $Rev: 8
"""

# BUILTIN modules
from uuid import UUID
from enum import Enum
from typing import Callable, Any
from datetime import datetime, UTC

# Third party modules
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Local modules
from .documentation import (metadata_example,
                            payment_documentation as pay_doc,
                            metadata_documentation as meta_doc)


# ---------------------------------------------------------
#
def utcnow():
    """ Return the current datetime with a UTC timezone.

    :return: Current UTC datetime.
    """
    return datetime.now(UTC)


# ---------------------------------------------------------
#
class MetadataSchema(BaseModel):
    """ Representation of Order metadata in the system.

    :ivar model_config: Current model config items.
    :ivar receiver: Callback receiver.
    :ivar order_id: Order identity.
    :ivar customer_id: Customer identity.
    """
    model_config = ConfigDict(json_schema_extra={"example": metadata_example})

    receiver: str = Field(**meta_doc['receiver'])
    order_id: str = Field(**meta_doc['order_id'])
    customer_id: str = Field(**meta_doc['customer_id'])

    @field_validator('*', mode='before')
    @classmethod
    def decode_values(cls, value: Any):
        """ Decode UUID value into a str. """
        return str(value) if isinstance(value, UUID) else value


# ---------------------------------------------------------
#
class Status(str, Enum):
    """ Payment result status.

    :ivar PEND: Pending payment state.
    :ivar REIM: Reimbursed state.
    :ivar PAID: Payment Paid state.
    :ivar FAIL: Payment failed state.
    """
    PEND = 'pending'
    REIM = 'reimbursed'
    PAID = 'paymentPaid'
    FAIL = 'paymentFailed'


# ------------------------------------------------------------------------
#
class MongoBase(BaseModel):
    """
    Class that handles conversions between MongoDB '_id' key
    and our own 'id' key.

    MongoDB uses ``_id`` as an internal default index key.
    We can use that to our advantage.

    :ivar model_config: MongoBase config items.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict) -> Callable:
        """ Convert "_id" (str object) into "id" (UUID object). """

        if not data:
            return data

        mongo_id = data.pop('_id', None)
        return cls(**dict(data, id=mongo_id))

    def to_mongo(self, **kwargs: dict) -> dict:
        """ Convert "id" (UUID object) into "_id" (str object). """
        parsed = self.model_dump(**kwargs)

        if '_id' not in parsed and 'id' in parsed:
            parsed['_id'] = str(parsed.pop('id'))

        return parsed


# ---------------------------------------------------------
#
class PaymentUpdateModel(MongoBase):
    """ Representation of an Order in the system.

    :ivar metadata: Metadata for the current order.
    :ivar transaction_id: Transaction identity.
    :ivar status: Current payment status.
    :ivar created: Datetime for created payment.
    """
    metadata: MetadataSchema
    transaction_id: UUID = Field(**pay_doc['transaction_id'])
    status: Status = Field(default=Status.PEND, **pay_doc['status'])
    created: datetime = Field(default_factory=utcnow, **pay_doc['created'])


# ---------------------------------------------------------
#
class PaymentModel(PaymentUpdateModel):
    """ Representation of a Payment in the system.

    :ivar id: Payment identity.
    """
    id: UUID = Field(**pay_doc['id'])
