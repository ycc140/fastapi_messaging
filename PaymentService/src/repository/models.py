# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-29 19:37:08
     $Rev: 45
"""

# BUILTIN modules
from uuid import UUID
from enum import Enum
from typing import Callable
from datetime import datetime

# Third party modules
from pydantic import BaseModel, BaseConfig, Field, UUID4, validator

# Local modules
from .documentation import payment_documentation as pay_doc
from ..web.api.documentation import (metadata_example,
                                     metadata_documentation as meta_doc)


# ---------------------------------------------------------
#
class MetadataSchema(BaseModel):
    """ Representation of Order metadata in the system. """
    receiver: str = Field(**meta_doc['receiver'])
    order_id: str = Field(**meta_doc['order_id'])
    customer_id: str = Field(**meta_doc['customer_id'])

    class Config:
        schema_extra = {"example": metadata_example}

    @validator('*', pre=True)
    def decode_values(cls, value):
        """ Decode UUID value into a str. """
        return str(value) if isinstance(value, UUID) else value


# ---------------------------------------------------------
#
class Status(str, Enum):
    """ Payment result status. """
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

    MongoDB uses `_id` as an internal default index key.
    We can use that to our advantage.
    """

    class Config(BaseConfig):
        """ basic config. """
        orm_mode = True
        allow_population_by_field_name = True

    # noinspection PyArgumentList
    @classmethod
    def from_mongo(cls, data: dict) -> Callable:
        """ Convert "_id" (str object) into "id" (UUID object). """

        if not data:
            return data

        mongo_id = data.pop('_id', None)
        return cls(**dict(data, id=mongo_id))

    def to_mongo(self, **kwargs) -> dict:
        """ Convert "id" (UUID object) into "_id" (str object). """
        parsed = self.dict(**kwargs)

        if '_id' not in parsed and 'id' in parsed:
            parsed['_id'] = str(parsed.pop('id'))

        return parsed


# ---------------------------------------------------------
#
class PaymentUpdateModel(MongoBase):
    """ Representation of an Order in the system. """
    metadata: MetadataSchema
    transaction_id: UUID4 = Field(**pay_doc['transaction_id'])
    status: Status = Field(default=Status.PEND, **pay_doc['status'])
    created: datetime = Field(default_factory=datetime.utcnow, **pay_doc['created'])


# ---------------------------------------------------------
#
class PaymentModel(PaymentUpdateModel):
    """ Representation of a Payment in the system. """
    id: UUID4 = Field(**pay_doc['id'])
