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
from enum import Enum
from uuid import UUID
from typing import List

# Third party modules
from pydantic import (BaseModel, Field, PositiveFloat,
                      conlist, ConfigDict, PositiveInt)

# Local modules
from ...repository.models import Status, MetadataSchema
from .documentation import (resource_example, billing_example,
                            metadata_documentation as meta_doc,
                            callback_documentation as callback)


# ---------------------------------------------------------
#
class ApiError(BaseModel):
    """ Define model for the http 400 exception (Unprocessable Entity).

    :ivar detail: The detailed exception reason.
    """
    detail: str = "Failed internal Microservice API call"


class ConnectError(BaseModel):
    """ Define model for the http 500 exception (INTERNAL_SERVER_ERROR).

    :ivar detail: The detailed exception reason.
    """
    detail: str = "Failed to connect to internal MicroService"


class HealthStatusError(BaseModel):
    """ Define model for the http 500 exception (INTERNAL_SERVER_ERROR).

    :ivar detail: The detailed exception reason.
    """
    detail: str = "HEALTH: resource connection(s) are down"


# ---------------------------------------------------------
#
class Products(str, Enum):
    """ Representation of valid products in the system.

    :ivar lasagna: Food product.
    :ivar cheese_burger: Food product.
    :ivar veil: Food product.
    :ivar vego_salad: Food product.
    """
    lasagna = 'Lasagna'
    cheese_burger = 'Double Cheeseburger'
    veil = 'Veil with glazed onions and blue cheese'
    vego_salad = 'Vegetarian Salad with healthy produce'


class OrderItem(BaseModel):
    """ Required order item parameters.

    :ivar product: Ordered product.
    :ivar quantity: Product quantity.
    """
    product: Products
    quantity: PositiveInt = 1


class OrderItems(BaseModel):
    """ A list of the ordered items.

    :ivar items: List of ordered items.
    """
    items: conlist(OrderItem, min_length=1)


# ---------------------------------------------------------
#
class PaymentPayload(OrderItems):
    """ Representation of a payment payload in the system.

    :ivar metadata: Order metadata in the system.
    """
    metadata: MetadataSchema


# ---------------------------------------------------------
#
class PaymentAcknowledge(BaseModel):
    """ Representation of a payment Acknowledge response in the system.

    :ivar status: Current payment status.
    :ivar order_id: Current order identity.
    """
    status: str = 'requestReceived'
    order_id: UUID = Field(**meta_doc['order_id'])


# ---------------------------------------------------------
#
class CreditCardSchema(BaseModel):
    """ Representation of Credit Card Billing Information in the system.

    :ivar model_config: Current model config items.
    :ivar CVV: CreditCard "hidden" key number.
    :ivar Bank: The bank issuing the credit Card.
    :ivar Name: Customer name.
    :ivar Expiry: Credit Card expiry date.
    :ivar Address: Customer address.
    :ivar Country: Customer country.
    :ivar MoneyRange: Current amount to pay.
    :ivar CardNumber: Credit Card number.
    :ivar IssuingNetwork: Credit Card type.
    """
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
    """ Representation of an external Billing payload in the system.

    :ivar caller_id: Caller identity.
    :ivar caller_id: Caller identity.
    :ivar caller_id: Caller identity.
    :ivar caller_id: Caller identity.
    """
    callback_url: str
    billing_info: CreditCardSchema
    amount: PositiveFloat = Field(example=9.54)
    caller_id: str = Field(**callback['caller_id'])


# ---------------------------------------------------------
#
class BillingCallback(BaseModel):
    """ Representation of an external Billing Callback in the system.

    :ivar status: Current Credit Card billing/reimburse status.
    :ivar caller_id: Caller identity.
    :ivar transaction_id: Transaction identity.
    """
    status: Status = Field(**callback['status'])
    caller_id: UUID = Field(**callback['caller_id'])
    transaction_id: UUID = Field(**callback['transaction_id'])


# -----------------------------------------------------------------------------
#
class HealthResourceModel(BaseModel):
    """ Representation of a health resources response.

    :ivar name: Resource name.
    :ivar status: Resource status
    """
    name: str
    status: bool


# -----------------------------------------------------------------------------
#
class HealthResponseModel(BaseModel):
    """ Representation of a health response.

    :ivar model_config: Health response OpenAPI documentation.
    :ivar name: Service name.
    :ivar version: Service version.
    :ivar status: Overall health status
    :ivar cert_remaining_days: Valid remaining TLS/SLL certificate days.
    :ivar resources: Status for individual resources.
    """
    model_config = ConfigDict(json_schema_extra={"example": resource_example})

    name: str
    version: str
    status: bool
    cert_remaining_days: int
    resources: List[HealthResourceModel]
