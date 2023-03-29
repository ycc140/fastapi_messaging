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
from typing import List, Optional

# Third party modules
from pydantic import (BaseModel, conint, conlist,
                      AnyHttpUrl, Field, UUID4, PositiveFloat)

# Local modules
from ...repository.models import Status, MetadataSchema
from .documentation import (resource_example, billing_example,
                            metadata_documentation as meta_doc,
                            callback_documentation as callback)


# ---------------------------------------------------------
#
class ApiError(BaseModel):
    """ Define model for a http 400 exception (Unprocessable Entity). """
    detail: str = "Failed internal Microservice API call"


class ConnectError(BaseModel):
    """ Define model for a http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"


class HealthStatusError(BaseModel):
    """ Define model for a http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "HEALTH: resource connection(s) are down"


# ---------------------------------------------------------
#
class Products(str, Enum):
    """ Representation of valid products in the system. """
    lasagna = 'Lasagna'
    cheese_burger = 'Double Cheeseburger'
    veil = 'Veil with glazed onions and blue cheese'
    vego_salad = 'Vegetarian Salad with healthy produce'


class OrderItem(BaseModel):
    """ Required order item parameters. """
    product: Products
    quantity: Optional[conint(ge=1, strict=True)] = 1


class OrderItems(BaseModel):
    """ A list of the ordered items. """
    items: conlist(OrderItem, min_items=1)


# ---------------------------------------------------------
#
class PaymentPayload(OrderItems):
    """ Representation of a payment payload in the system. """
    metadata: MetadataSchema


# ---------------------------------------------------------
#
class PaymentAcknowledge(BaseModel):
    """ Representation of a payment Acknowledge response in the system. """
    status: str = 'requestReceived'
    order_id: UUID4 = Field(**meta_doc['order_id'])


# ---------------------------------------------------------
#
class CreditCardSchema(BaseModel):
    """ Representation of Credit Card Billing Information in the system. """
    CVV: str
    Bank: str
    Name: str
    Expiry: str
    Address: str
    Country: str
    MoneyRange: str
    CardNumber: str
    IssuingNetwork: str

    class Config:
        schema_extra = {"example": billing_example}


# ---------------------------------------------------------
#
class BillingPayload(BaseModel):
    """ Representation of an external Billing payload in the system. """
    callback_url: AnyHttpUrl
    billing_info: CreditCardSchema
    amount: PositiveFloat = Field(example=9.54)
    caller_id: str = Field(**callback['caller_id'])


# ---------------------------------------------------------
#
class BillingCallback(BaseModel):
    """ Representation of an external Billing Callback in the system. """
    status: Status = Field(**callback['status'])
    caller_id: UUID4 = Field(**callback['caller_id'])
    transaction_id: UUID4 = Field(**callback['transaction_id'])


# -----------------------------------------------------------------------------
#
class ResourceSchema(BaseModel):
    """ Representation of a  health resources response.

    :ivar name: Resource name.
    :ivar status: Resource status
    """
    name: str
    status: bool


# -----------------------------------------------------------------------------
#
class HealthSchema(BaseModel):
    """ Representation of a  health response.

    :ivar name: Service name.
    :ivar version: Service version.
    :ivar status: Overall health status
    :ivar resources: Status for individual resources..
    """
    name: str
    version: str
    status: bool
    resources: List[ResourceSchema]

    class Config:
        schema_extra = {"example": resource_example}
