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
from datetime import datetime
from typing import Optional, List

# Third party modules
from pydantic import UUID4
from fastapi import HTTPException
from httpx import AsyncClient, ConnectTimeout

# Local modules
from ..config.setup import config
from ..repository.url_cache import UrlCache
from ..web.api.schemas import OrderResponse
from .schemas import PaymentPayload, MetadataSchema
from ..repository.order_data_adapter import OrdersRepository
from ..repository.models import Status, OrderItems, OrderModel, StateUpdateSchema


# ------------------------------------------------------------------------
#
class OrderApiLogic:
    """
    This class implements the OrderService web API business logic layer.
    """

    # ---------------------------------------------------------
    #
    def __init__(
            self,
            id: UUID4,
            created: datetime,
            items: OrderItems,
            updated: List[StateUpdateSchema],
            status: Status, customer_id: UUID4,
            kitchen_id: Optional[UUID4] = None,
            delivery_id: Optional[UUID4] = None,
    ):
        """ The class initializer.

        :param id: Order id.
        :param created: Order created timestamp.
        :param items: Ordered items.
        :param status: Current order status.
        :param customer_id: The individual that created the order.
        :param kitchen_id: Does not exist before the scheduled state.
        :param delivery_id: Does not exist before the dispatched state.
        """
        self._id = id
        self.items = items
        self._status = status
        self.updated = updated
        self._created = created
        self.kitchen_id = kitchen_id
        self.delivery_id = delivery_id
        self.customer_id = customer_id

        # Initialize objects.
        self.repo = OrdersRepository()
        self.cache = UrlCache(config.redis_url)

    # ---------------------------------------------------------
    #
    @property
    def id(self) -> UUID4:
        """ Return order id.

        :return: order id.
        """
        return self._id

    # ---------------------------------------------------------
    #
    @property
    def created(self) -> datetime:
        """ Return current order creation time.

        :return: datetime when the order was created.
        """
        return self._created

    # ---------------------------------------------------------
    #
    @property
    def status(self) -> Status:
        """ Return current order status.

        :return: current status
        """
        return self._status

    # ---------------------------------------------------------
    #
    async def _pay(self) -> None:
        """ Trigger payment of ordered items.

        :raise HTTPException [400]: when PaymentService response code != 201.
        :raise HTTPException [500]: when connection with PaymentService failed.
        """
        meta = MetadataSchema(order_id=self.id,
                              customer_id=self.customer_id,
                              receiver=f'{config.service_name}')
        payment = PaymentPayload(metadata=meta, **self.dict())

        try:
            root = await self.cache.get('PaymentService')

            async with AsyncClient() as client:
                url = f"{root}/v1/payments"
                response = await client.post(url=url,
                                             json=payment.dict(),
                                             timeout=config.url_timeout)

            if response.status_code != 201:
                errmsg = f"Failed PaymentService POST request for URL {url} with Order ID "  \
                         f"{self.id} - [{response.status_code}: {response.json()['detail']}]."
                raise HTTPException(status_code=400, detail=errmsg)

        except ConnectTimeout:
            errmsg = f'No connection with PaymentService on URL {url}'
            raise HTTPException(status_code=500, detail=errmsg)

    # ---------------------------------------------------------
    #
    async def _reimburse(self) -> None:
        """ Trigger reimbursement of cancelled order items.

        :raise HTTPException [400]: when PaymentService response code != 201.
        :raise HTTPException [500]: when connection with PaymentService failed.
        """
        meta = MetadataSchema(order_id=self.id,
                              customer_id=self.customer_id,
                              receiver=f'{config.service_name}')
        payment = PaymentPayload(metadata=meta, **self.dict())

        try:
            root = await self.cache.get('PaymentService')

            async with AsyncClient() as client:
                url = f"{root}/v1/payments/reimburse"
                response = await client.post(url=url,
                                             json=payment.dict(),
                                             timeout=config.url_timeout)

            if response.status_code != 201:
                errmsg = f"Failed PaymentService POST request for URL {url} with Order ID "  \
                         f"{self.id} - [{response.status_code}: {response.json()['detail']}]."
                raise HTTPException(status_code=400, detail=errmsg)

        except ConnectTimeout:
            errmsg = f'No connection with PaymentService on URL {url}'
            raise HTTPException(status_code=500, detail=errmsg)

    # ---------------------------------------------------------
    #
    async def create(self) -> OrderResponse:
        """ Charge the Customers Credit Card and create a new order in DB.

        :raise HTTPException [400]: when PaymentService response code != 201.
        :raise HTTPException [500]: when connection with PaymentService failed.
        :raise HTTPException [400]: when create order in DB api_db.orders failed.
        """
        await self._pay()

        # Create a new Order document in DB.
        db_order = OrderModel(**self.dict())
        successful = await self.repo.create(db_order)

        if not successful:
            errmsg = f"Create failed for {self.id=} in api_db.orders"
            raise HTTPException(status_code=400, detail=errmsg)

        return OrderResponse(**db_order.dict())

    # ---------------------------------------------------------
    #
    async def cancel(self) -> OrderResponse:
        """ Cancel current order.

        NOTE: this can only be done before a driver is available (status DRAV).

        :raise HTTPException [400]: when cancel request came too late.
        :raise HTTPException [400]: when Order update in DB api_db.orders failed.
        """
        await self._reimburse()

        if self.status != Status.DESC:
            errmsg = f'Could not cancel order with id {self.id} and {self.status=}'
            raise HTTPException(status_code=400, detail=errmsg)

        # Prepare order update.
        db_order = OrderModel(**self.dict())
        db_order.status = Status.ORCA
        db_order.updated.append(StateUpdateSchema(status=db_order.status))

        # Update Order status in DB.
        successful = await self.repo.update(db_order)

        if not successful:
            errmsg = f"Failed updating {self.id=} in api_db.orders"
            raise HTTPException(status_code=400, detail=errmsg)

        return OrderResponse(**db_order.dict())

    # ---------------------------------------------------------
    #
    async def delete(self) -> None:
        """ Delete current order.

        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """
        response = await self.repo.delete(self.id)

        if response.deleted_count == 0:
            errmsg = f"{self.id=} not found in api_db.orders"
            raise HTTPException(status_code=404, detail=errmsg)

    # ---------------------------------------------------------
    #
    def dict(self) -> dict:
        """ Return essential class parameters using base class types.

        :return: Base class types representation of the class.
        """
        return {
            'id': str(self.id),
            'items': self.items,
            'status': self.status,
            'created': str(self.created),
            'customer_id': str(self.customer_id),
            'kitchen_id': (str(self.kitchen_id) if self.kitchen_id else None),
            'delivery_id': (str(self.delivery_id) if self.delivery_id else None),
            'updated': list(map(lambda elem: {'status': elem['status'],
                                              'when': str(elem['when'])}, self.updated))}
