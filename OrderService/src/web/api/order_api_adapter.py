# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-30 13:14:04
     $Rev: 48
"""

# BUILTIN modules
from typing import List

# Third party modules
from pydantic import UUID4
from fastapi import HTTPException

# Local modules
from ...repository.models import OrderModel
from .schemas import OrderResponse, OrderPayload
from ...business.request_handler import OrderApiLogic
from ...repository.order_data_adapter import OrdersRepository


# ------------------------------------------------------------------------
#
class OrdersApi:
    """
    This class implements the web API layer adapter.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: OrdersRepository):
        """ The class initializer.

        :param repository: Data layer handler object.
        """
        self.repo = repository

    # ---------------------------------------------------------
    #
    async def _order_of(self, order_id: UUID4) -> OrderModel:
        """ Return specified order.

        :param order_id: Order id for order to find.
        :return: Found Order object.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """
        db_order = await self.repo.read(order_id)

        if not db_order:
            errmsg = f"{order_id=} not found in DB api_db.orders"
            raise HTTPException(status_code=404, detail=errmsg)

        return db_order

    # ---------------------------------------------------------
    #
    async def list_orders(self) -> List[OrderResponse]:
        """ List all existing orders in DB api_db.orders.

        Sorted on creation timestamp in descending order.

        :return: List of found orders.
        """
        return await self.repo.read_all()

    # ---------------------------------------------------------
    #
    async def get_order(self, order_id: UUID4) -> OrderResponse:
        """ Return specified order.

        :param order_id: Order id for order to find.
        :return: Found Order object.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """
        db_order = await self._order_of(order_id)
        return OrderResponse(**db_order.dict())

    # ---------------------------------------------------------
    #
    async def create_order(self, payload: OrderPayload) -> OrderResponse:
        """ Create a new order in DB and make a payment request.

        :param payload: Incoming Order request.
        :return: Created Order object.
        :raise HTTPException [400]: when PaymentService response code != 202.
        :raise HTTPException [500]: when connection with PaymentService failed.
        :raise HTTPException [400]: when create order in DB api_db.orders failed.
        """
        db_order = OrderModel(**payload.dict())
        order = OrderApiLogic(repository=self.repo, **db_order.dict())
        return await order.create()

    # ---------------------------------------------------------
    #
    async def cancel_order(self, order_id: UUID4) -> OrderResponse:
        """ Cancel specified order.

        :param order_id: id for order to cancel.
        :return: Found Order object.
        :raise HTTPException [400]: when failed to update DB api_db.orders.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """
        db_order = await self._order_of(order_id)
        order = OrderApiLogic(repository=self.repo, **db_order.dict())
        return await order.cancel()

    # ---------------------------------------------------------
    #
    async def delete_order(self, order_id: UUID4) -> None:
        """ Delete specified order.

        :param order_id: id for order to delete.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """
        db_order = await self._order_of(order_id)
        order = OrderApiLogic(repository=self.repo, **db_order.dict())
        await order.delete()
