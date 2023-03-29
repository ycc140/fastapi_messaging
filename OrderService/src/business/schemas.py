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
from enum import Enum
from uuid import UUID

# Third party modules
from pydantic import BaseModel, validator, Field

# Local modules
from ..repository.models import OrderItems
from ..web.api.documentation import (metadata_example, address_example,
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
class PaymentPayload(OrderItems):
    """ Representation of a payment payload in the system. """
    metadata: MetadataSchema


# ---------------------------------------------------------
#
class PaymentStatus(str, Enum):
    """ Representation of valid payment response states. """

    PAID = "paymentPaid"
    FAILED = "paymentFailed"


# ---------------------------------------------------------
#
class PaymentResponse(BaseModel):
    """ Representation of a payment response in the system. """
    metadata: MetadataSchema
    status: PaymentStatus = Field(send_example=PaymentStatus.PAID)


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

    class Config:
        schema_extra = {"example": address_example}


# ---------------------------------------------------------
#
class DeliveryPayload(OrderItems):
    """ Representation of a Delivery payload in the system. """
    metadata: MetadataSchema
    address: CustomerAddressSchema
