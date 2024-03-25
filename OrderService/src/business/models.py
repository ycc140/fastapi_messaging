# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-24 19:33:51
     $Rev: 72
"""

# BUILTIN modules
from uuid import UUID
from typing import Any

# Third party modules
from pydantic import BaseModel, field_validator

# Local modules
from ..repository.models import OrderItems, Status


# ---------------------------------------------------------
#
class MetadataSchema(BaseModel):
    """ Representation of Order metadata in the system.

    :ivar receiver: Callback receiver.
    :ivar order_id: Order identity.
    :ivar customer_id: Customer identity.
    """
    receiver: str
    order_id: str
    customer_id: str

    @field_validator('*', mode='before')
    @classmethod
    def decode_values(cls, value: Any):
        """ Decode UUID value into a str. """
        return str(value) if isinstance(value, UUID) else value


# ---------------------------------------------------------
#
class PaymentPayload(OrderItems):
    """ Representation of a payment payload in the system.

    :ivar metadata: Order metadata in the system.
    """
    metadata: MetadataSchema


# ---------------------------------------------------------
#
class PaymentResponse(BaseModel):
    """ Representation of a payment response in the system.

    :ivar status: Order state.
    :ivar metadata: Order metadata in the system.
    """
    status: Status
    metadata: MetadataSchema


# ---------------------------------------------------------
#
class KitchenPayload(OrderItems):
    """ Representation of a Kitchen payload in the system.

    :ivar metadata: Order metadata in the system.
    """
    metadata: MetadataSchema


# ---------------------------------------------------------
#
class CustomerAddressSchema(BaseModel):
    """ Representation of Customer Address Information in the system.

    :ivar name: Customer name.
    :ivar city: Customer city.
    :ivar street: Customer street.
    :ivar zipcode: Customer zipcode.
    """
    name: str
    city: str
    street: str
    zipcode: str


# ---------------------------------------------------------
#
class DeliveryPayload(OrderItems):
    """ Representation of a Delivery payload in the system.

    :ivar metadata: Order metadata in the system.
    :ivar address: Customer delivery address.
    """
    metadata: MetadataSchema
    address: CustomerAddressSchema
