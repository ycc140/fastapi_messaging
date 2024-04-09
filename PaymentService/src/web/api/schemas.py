# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-09 05:37:36
     $Rev: 3
"""

# BUILTIN modules
from uuid import UUID
from enum import Enum
from typing import List, Optional

# Third party modules
from pydantic import (BaseModel, ConfigDict, Field, conint,
                      conlist, AnyHttpUrl, PositiveFloat)

# Local modules
from ...repository.models import Status, MetadataSchema
from .documentation import (health_example, billing_example,
                            metadata_documentation as meta_doc,
                            callback_documentation as callback)


# ---------------------------------------------------------
#
class ApiError(BaseModel):
    """ Define model for the http 400 exception (Unprocessable Entity). """
    detail: str = "Failed internal Microservice API call"


class ConnectError(BaseModel):
    """ Define model for the http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"


class HealthStatusError(BaseModel):
    """ Define model for the http 500 exception (INTERNAL_SERVER_ERROR). """
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
    items: conlist(OrderItem, min_length=1)


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
    order_id: UUID = Field(**meta_doc['order_id'])


# ---------------------------------------------------------
#
class CreditCardSchema(BaseModel):
    """ Representation of Credit Card Billing Information in the system. """
    model_config = ConfigDict(json_schema_extra={"example": billing_example})

    CVV: str
    Bank: str
    Name: str
    Expiry: str
    Address: str
    Country: str
    MoneyRange: str
    CardNumber: str
    IssuingNetwork: str


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
    caller_id: UUID = Field(**callback['caller_id'])
    transaction_id: UUID = Field(**callback['transaction_id'])


# -----------------------------------------------------------------------------
#
class ResourceSchema(BaseModel):
    """ Representation of a health resources response.

    :ivar name: Resource name.
    :ivar status: Resource status
    """
    name: str
    status: bool


# -----------------------------------------------------------------------------
#
class HealthSchema(BaseModel):
    """ Representation of a health response.

    :ivar name: Service name.
    :ivar version: Service version.
    :ivar status: Overall health status
    :ivar resources: Status for individual resources.
    """
    model_config = ConfigDict(json_schema_extra={"example": health_example})

    name: str
    version: str
    status: bool
    resources: List[ResourceSchema]
