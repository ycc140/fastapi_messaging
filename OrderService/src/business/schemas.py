# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-04-02 14:01:36
     $Rev: 57
"""

# BUILTIN modules
from uuid import UUID

# Third party modules
from pydantic import BaseModel, validator

# Local modules
from ..repository.models import OrderItems, Status


# ---------------------------------------------------------
#
class MetadataSchema(BaseModel):
    """ Representation of Order metadata in the system. """
    receiver: str
    order_id: str
    customer_id: str

    @validator('*', pre=True)
    def decode_values(cls, value):
        """ Decode UUID value into a str. """
        return str(value) if isinstance(value, UUID) else value


# ---------------------------------------------------------
#
class PaymentPayload(OrderItems):
    """ Representation of a payment payload in the system. """
    metadata: MetadataSchema


# ---------------------------------------------------------
#
class PaymentResponse(BaseModel):
    """ Representation of a payment response in the system. """
    metadata: MetadataSchema
    status: Status


# ---------------------------------------------------------
#
class KitchenPayload(OrderItems):
    """ Representation of a Kitchen payload in the system. """
    metadata: MetadataSchema


# ---------------------------------------------------------
#
class CustomerAddressSchema(BaseModel):
    """ Representation of Customer Address Information in the system. """
    name: str
    city: str
    street: str
    zipcode: str


# ---------------------------------------------------------
#
class DeliveryPayload(OrderItems):
    """ Representation of a Delivery payload in the system. """
    metadata: MetadataSchema
    address: CustomerAddressSchema
