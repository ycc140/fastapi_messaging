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
from datetime import datetime
from typing import Optional, List

# Third party modules
from pydantic import BaseModel, ConfigDict, Field

# Local modules
from ..api.documentation import health_example
from ...repository.models import Status, OrderItems
from ...repository.documentation import order_documentation as order_doc


# -----------------------------------------------------------------------------
#
class NotFoundError(BaseModel):
    """ Define model for the http 404 exception (Not Found). """
    detail: str = "Order not found in DB"


class FailedUpdateError(BaseModel):
    """ Define model for the http 400 exception (Unprocessable Entity). """
    detail: str = "Failed updating Order in DB"


class ConnectError(BaseModel):
    """ Define model for the http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"


class HealthStatusError(BaseModel):
    """ Define model for the http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "HEALTH: resource connection(s) are down"


# ---------------------------------------------------------
#
class OrderPayload(OrderItems):
    """ Payload parameters required when creating an order. """
    customer_id: UUID = Field(**order_doc['customer_id'])


# ---------------------------------------------------------
#
class OrderResponse(OrderItems):
    """ Expected default order response parameters. """
    id: UUID = Field(**order_doc['id'])
    status: Status = Field(**order_doc['status'])
    created: datetime = Field(**order_doc['created'])
    customer_id: UUID = Field(**order_doc['customer_id'])
    kitchen_id: Optional[UUID] = Field(**order_doc['kitchen_id'])
    delivery_id: Optional[UUID] = Field(**order_doc['delivery_id'])


# ------------------------------------------------------------------------
#
class ValidStatus(BaseModel):
    """ Used for validation of received status responses. """
    status: Status


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
    :ivar status: Overall health status
    :ivar version: Service version.
    :ivar resources: Status for individual resources.
    """
    model_config = ConfigDict(json_schema_extra={"example": health_example})

    status: bool
    version: str
    name: str
    resources: List[ResourceSchema]
