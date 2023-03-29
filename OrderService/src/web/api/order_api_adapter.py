
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
class OrdersServiceApi:
    """
    This class implements the web API layer adapter.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, orders_repository: OrdersRepository):
        """ The class initializer.

        :param orders_repository: Data layer handler object.
        """
        self.repo = orders_repository

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
    @staticmethod
    async def create_order(payload: OrderPayload) -> OrderResponse:
        """ Create a new order in DB and make a payment request.

        :param payload: Incoming Order request.
        :return: Created Order object.
        :raise HTTPException [400]: when PaymentService response code != 202.
        :raise HTTPException [500]: when connection with PaymentService failed.
        :raise HTTPException [400]: when create order in DB api_db.orders failed.
        """
        db_order = OrderModel(**payload.dict())
        order = OrderApiLogic(**db_order.dict())
        return await order.create()

    # ---------------------------------------------------------
    #
    async def get_order(self, order_id: UUID4) -> OrderResponse:
        """ Return specified order.

        :param order_id: Order id for order to find.
        :return: Found Order object.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """
        response = await self.repo.read(order_id)

        if not response:
            errmsg = f"{order_id=} not found in DB api_db.orders"
            raise HTTPException(status_code=404, detail=errmsg)

        return OrderResponse(**response.dict())

    # ---------------------------------------------------------
    #
    async def cancel_order(self, order_id: UUID4) -> OrderResponse:
        """ Cancel specified order.

        :param order_id: id for order to cancel.
        :return: Found Order object.
        :raise HTTPException [400]: when failed to update DB api_db.orders.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """
        response = await self.get_order(order_id)
        db_order = OrderModel(**response.dict())
        order = OrderApiLogic(**db_order.dict())
        return await order.cancel()

    # ---------------------------------------------------------
    #
    async def delete_order(self, order_id: UUID4) -> None:
        """ Delete specified order.

        :param order_id: id for order to delete.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """
        response = await self.get_order(order_id)
        order = OrderApiLogic(**response.dict())
        await order.delete()
