# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-22 20:51:42
     $Rev: 69
"""

# BUILTIN modules
from uuid import UUID
from typing import List

# Third party modules
from fastapi.responses import Response
from fastapi import APIRouter, status, Depends

# Local modules
from .order_api_adapter import OrdersApi
from .documentation import order_id_documentation
from ...tools.security import validate_authentication
from ...repository.order_data_adapter import orders_repository
from .models import (OrderPayload, OrderResponse,
                     NotFoundError, FailedUpdateError, ConnectError)

# Constants
ROUTER = APIRouter(prefix="/v1/orders", tags=["Orders"])
""" Order API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post(
    '',
    response_model=OrderResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        400: {"model": FailedUpdateError}},
    dependencies=[Depends(validate_authentication)]
)
async def create_order(payload: OrderPayload) -> OrderResponse:
    """ **Create a new Order in the DB and trigger a payment.**

    :param payload: Current order payload.
    :return: Order create response.
    """
    service = OrdersApi(orders_repository)
    return await service.create_order(payload)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {"model": NotFoundError},
        400: {"model": FailedUpdateError}},
    dependencies=[Depends(validate_authentication)]
)
async def cancel_order(order_id: UUID = order_id_documentation) -> OrderResponse:
    """
    **Cancel Order for matching order_id in the DB and trigger a reimbursement.**

    :param order_id: Current order_id.
    :return: Order cancel response.
    """
    service = OrdersApi(orders_repository)
    return await service.cancel_order(order_id)


# ---------------------------------------------------------
#
@ROUTER.get(
    "",
    response_model=List[OrderResponse],
    dependencies=[Depends(validate_authentication)]
)
async def get_all_orders() -> List[OrderResponse]:
    """ **Read all Orders from the DB sorted on created timestamp.**

    :return: All orders.
    """
    service = OrdersApi(orders_repository)
    return await service.list_orders()


# ---------------------------------------------------------
#
@ROUTER.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={404: {"model": NotFoundError}},
    dependencies=[Depends(validate_authentication)]
)
async def get_order(order_id: UUID = order_id_documentation) -> OrderResponse:
    """ **Read Order for matching order_id from the DB.**

    :param order_id: Current order_id.
    :return: Order query response.
    """
    service = OrdersApi(orders_repository)
    return await service.get_order(order_id)


# ---------------------------------------------------------
#
@ROUTER.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": NotFoundError}},
    dependencies=[Depends(validate_authentication)],
    response_description='Order was successfully deleted in the DB.'
)
async def delete_order(order_id: UUID = order_id_documentation) -> Response:
    """ **Delete Order for matching order_id from the DB.**

    :param order_id: Current order_id.
    :return: Order delete response (None).
    """
    service = OrdersApi(orders_repository)
    await service.delete_order(order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
