# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-19 11:40:10
     $Rev: 7
"""

# BUILTIN modules
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# Third party modules
from fastapi import HTTPException
from httpx import AsyncClient, ConnectTimeout

# Local modules
from ..web.api.models import OrderResponse
from ..core.setup import config, SSL_CONTEXT
from ..repository.interface import IRepository
from ..repository.url_cache import UrlServiceCache
from .models import PaymentPayload, MetadataSchema
from ..repository.models import Status, OrderItems, OrderModel, StateUpdateSchema

# Constants
HDR_DATA = {'Content-Type': 'application/json',
            'X-API-Key': f'{config.service_api_key}'}


# ------------------------------------------------------------------------
#
class OrderApiLogic:
    """
    This class implements the OrderService web API business logic layer.

    :ivar _id: Order id.
    :type _id: `UUID`
    :ivar items: Ordered items.
    :type items: `OrderItems`
    :ivar _status: Current order status.
    :type _status: `Status`
    :ivar updated: List of updated items.
    :type updated: List[StateUpdateSchema]
    :ivar _created: Order created timestamp.
    :type _created: `datetime`
    :ivar kitchen_id: It does not exist before the scheduled state.
    :type kitchen_id: `UUID`
    :ivar delivery_id: It does not exist before the dispatched state.
    :type delivery_id: `UUID`
    :ivar customer_id: Customer identity.
    :type customer_id: `UUID`
    :ivar repo: DB repository.
    :type repo: `IRepository`
    """

    # ---------------------------------------------------------
    #
    def __init__(
            self,
            id: UUID,
            created: datetime,
            items: OrderItems,
            repository: IRepository,
            updated: List[StateUpdateSchema],
            status: Status, customer_id: UUID,
            kitchen_id: Optional[UUID] = None,
            delivery_id: Optional[UUID] = None,
    ):
        """ The class initializer.

        :param id: Order id.
        :param created: Order created timestamp.
        :param items: Ordered items.
        :param repository: Current repository.
        :param updated: Updated items.
        :param status: Current order status.
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
        self.repo = repository

    # ---------------------------------------------------------
    #
    @property
    def id(self) -> UUID:
        """ Return order id.

        :return: Order id.
        """
        return self._id

    # ---------------------------------------------------------
    #
    @property
    def created(self) -> datetime:
        """ Return current order creation time.

        :return: Datetime when the order was created.
        """
        return self._created

    # ---------------------------------------------------------
    #
    @property
    def status(self) -> Status:
        """ Return current order status.

        :return: Current status
        """
        return self._status

    # ---------------------------------------------------------
    #
    async def _pay(self):
        """ Trigger payment of ordered items.

        :raise HTTPException [400]: When PaymentService response code != 202.
        :raise HTTPException [500]: When connection with PaymentService failed.
        """
        cache = UrlServiceCache(config.redis_url)
        meta = MetadataSchema(order_id=self.id,
                              customer_id=self.customer_id,
                              receiver=f'{config.service_name}')
        payment = PaymentPayload(metadata=meta, **self.dict())

        try:
            root = await cache.get('PaymentService')

            async with AsyncClient(verify=SSL_CONTEXT,
                                   headers=HDR_DATA) as client:
                url = f"{root}/v1/payments"
                response = await client.post(url=url,
                                             json=payment.model_dump(),
                                             timeout=config.url_timeout)

            if response.status_code != 202:
                errmsg = (f"Failed PaymentService POST request for URL {url} with Order ID "
                          f"{self.id} - [{response.status_code}: {response.json()['detail']}].")
                raise HTTPException(status_code=400, detail=errmsg)

        except ConnectTimeout:
            errmsg = f'No connection with PaymentService on URL {url}'
            raise HTTPException(status_code=500, detail=errmsg)

        finally:
            await cache.close()

    # ---------------------------------------------------------
    #
    async def _reimburse(self):
        """ Trigger reimbursement of canceled order items.

        :raise HTTPException [400]: When PaymentService response code != 202.
        :raise HTTPException [500]: When connection with PaymentService failed.
        """
        cache = UrlServiceCache(config.redis_url)
        meta = MetadataSchema(order_id=self.id,
                              customer_id=self.customer_id,
                              receiver=f'{config.service_name}')
        payment = PaymentPayload(metadata=meta, **self.dict())

        try:
            root = await cache.get('PaymentService')

            async with AsyncClient(verify=SSL_CONTEXT,
                                   headers=HDR_DATA) as client:
                url = f"{root}/v1/payments/reimburse"
                response = await client.post(url=url,
                                             json=payment.model_dump(),
                                             timeout=config.url_timeout)

            if response.status_code != 202:
                errmsg = (f"Failed PaymentService POST request for URL {url} with Order ID "
                          f"{self.id} - [{response.status_code}: {response.json()['detail']}].")
                raise HTTPException(status_code=400, detail=errmsg)

        except ConnectTimeout:
            errmsg = f'No connection with PaymentService on URL {url}'
            raise HTTPException(status_code=500, detail=errmsg)

        finally:
            await cache.close()

    # ---------------------------------------------------------
    #
    async def create(self) -> OrderResponse:
        """ Charge the Customers Credit Card and create a new order in DB.

        :return: Order response.
        :raise HTTPException [400]: When PaymentService response code != 202.
        :raise HTTPException [500]: When connection with PaymentService failed.
        :raise HTTPException [400]: When create order in DB api_db.orders failed.
        """
        await self._pay()

        # Create a new Order document in DB.
        db_order = OrderModel(**self.dict())
        successful = await self.repo.create(db_order)

        if not successful:
            errmsg = f"Create failed for {self.id=} in api_db.orders"
            raise HTTPException(status_code=400, detail=errmsg)

        return OrderResponse(**db_order.model_dump())

    # ---------------------------------------------------------
    #
    async def cancel(self) -> OrderResponse:
        """ Cancel the current order.

        NOTE: this can only be done before a driver is available (status DRAV).

        :return: Order response.
        :raise HTTPException [400]: When cancel request came too late.
        :raise HTTPException [400]: When Order update in DB api_db.orders failed.
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

        return OrderResponse(**db_order.model_dump())

    # ---------------------------------------------------------
    #
    async def delete(self):
        """ Delete current order.

        :raise HTTPException [404]: When Order not found in DB api_db.orders.
        """
        successful = await self.repo.delete(self.id)

        if not successful:
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
