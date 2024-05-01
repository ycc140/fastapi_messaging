# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-05-01 02:28:35
     $Rev: 15
"""

# BUILTIN modules
from uuid import UUID
from typing import List

# Third party modules
from fastapi import HTTPException

# Local modules
from ...repository.models import OrderModel
from ...business.models import PaymentResponse
from ...repository.interface import IRepository
from .models import OrderResponse, OrderPayload
from ...business.request_handler import OrderApiLogic
from ...business.response_handler import OrderPaymentResponseLogic


# ------------------------------------------------------------------------
#
class OrderApiAdapter:
    """ This class is the Order primary adapter API implementation.

    :ivar repo: The order repository object.
    :type repo: `IRepository`
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: IRepository):
        """ The class initializer.

        :param repository: The order repository object.
        """
        self.repo = repository

    # ---------------------------------------------------------
    #
    async def _order_of(self, order_id: UUID) -> OrderModel:
        """ Return specified order.

        :param order_id: Order id for order to find.
        :return: The found Order object.
        :raise HTTPException [404]: When Order not found in DB api_db.orders.
        """
        db_order = await self.repo.read(order_id)

        if not db_order:
            errmsg = f"order_id '{order_id}' not found in DB api_db.orders"
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
    async def get_order(self, order_id: UUID) -> OrderResponse:
        """ Return specified order.

        :param order_id: Order id for order to find.
        :return: The found Order object.
        :raise HTTPException [404]: When Order not found in DB api_db.orders.
        """
        db_order = await self._order_of(order_id)
        return OrderResponse(**db_order.model_dump())

    # ---------------------------------------------------------
    #
    async def create_order(self, payload: OrderPayload) -> OrderResponse:
        """ Create a new order in DB and make a payment request.

        :param payload: Incoming Order request.
        :return: The created Order object.
        :raise HTTPException [400]: When PaymentService response code != 202.
        :raise HTTPException [500]: When connection with PaymentService failed.
        :raise HTTPException [400]: When create order in DB api_db.orders failed.
        """
        db_order = OrderModel(**payload.model_dump())
        order = OrderApiLogic(repository=self.repo, **db_order.model_dump())
        return await order.create()

    # ---------------------------------------------------------
    #
    async def cancel_order(self, order_id: UUID) -> OrderResponse:
        """ Cancel a specified order.

        :param order_id: ID for order to cancel.
        :return: The found Order object.
        :raise HTTPException [400]: When failed to update DB api_db.orders.
        :raise HTTPException [404]: When Order not found in DB api_db.orders.
        """
        db_order = await self._order_of(order_id)
        order = OrderApiLogic(repository=self.repo, **db_order.model_dump())
        return await order.cancel()

    # ---------------------------------------------------------
    #
    async def delete_order(self, order_id: UUID) -> None:
        """ Delete specified order.

        :param order_id: ID for the order to delete.
        :raise HTTPException [404]: When Order not found in DB api_db.orders.
        """
        db_order = await self._order_of(order_id)
        order = OrderApiLogic(repository=self.repo, **db_order.model_dump())
        await order.delete()
