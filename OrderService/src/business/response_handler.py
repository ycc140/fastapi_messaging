# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-04-01 17:51:19
     $Rev: 55
"""

# BUILTIN modules
from uuid import UUID

# Third party modules
from loguru import logger
from httpx import AsyncClient, ConnectTimeout

# Local modules
from ..config.setup import config
from ..repository.url_cache import UrlCache
from .schemas import KitchenPayload, DeliveryPayload
from ..repository.order_data_adapter import OrdersRepository
from ..repository.models import Status, OrderModel, StateUpdateSchema


# ------------------------------------------------------------------------
#
class OrderResponseLogic:
    """
    This class implements the OrderService business logic layer
    for RabbitMQ response messages.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, cache: UrlCache, repository: OrdersRepository):
        """ The class initializer.

        :param repository: Data layer handler object.
        """
        self.cache = cache
        self.repo = repository

    # ---------------------------------------------------------
    #
    async def _update_order_in_db(self, order: OrderModel):
        """ Update Order in DB.

        :param order: Current Order.
        """
        successful = await self.repo.update(order)

        if not successful:
            errmsg = f"Failed updating {order.id=} in api_db.orders"
            raise RuntimeError(errmsg)

        log = getattr(logger, ('error' if order.status == 'paymentFailed' else 'info'))
        log(f'Stored {order.status=} in DB for {order.id=}.')

    # ---------------------------------------------------------
    #
    async def _handle_successful_payment(self, message: dict, order: OrderModel):
        """ Payment was successful so get Customer Address and request DeliveryService work.

        :param message: PaymentService response message.
        :param order: Current Order.
        """
        try:
            root = await self.cache.get('CustomerService')

            # Get Customer Address information.
            async with AsyncClient() as client:
                service = 'CustomerService'
                url = f"{root}/v1/customers/{order.customer_id}/address"
                resp = await client.get(url=url, timeout=config.url_timeout)

            if resp.status_code != 200:
                errmsg = f"Failed {service} POST request for URL {url} - " \
                         f"[{resp.status_code}: {resp.json()['detail']}]."
                raise RuntimeError(errmsg)

            payload = DeliveryPayload(metadata=message['metadata'],
                                      address=resp.json(), **order.dict())

            root = await self.cache.get('DeliveryService')

            # Request DeliveryService work.
            async with AsyncClient() as client:
                service = 'DeliveryService'
                url = f"{root}/v1/deliveries"
                resp = await client.post(url=url, json=payload.dict(),
                                         timeout=config.url_timeout)

            if resp.status_code != 202:
                errmsg = f"Failed {service} POST request for URL {url} - " \
                         f"[{resp.status_code}: {resp.json()['detail']}]."
                raise RuntimeError(errmsg)

            data = resp.json()
            order.status = data['status']
            order.delivery_id = data['delivery_id']
            order.updated.append(StateUpdateSchema(status=order.status))
            await self._update_order_in_db(order)

        except ConnectTimeout:
            errmsg = f'No connection with {service} on URL {url}'
            raise ConnectionError(errmsg)

    # ---------------------------------------------------------
    #
    async def _handle_delivery_ready(self, message: dict, order: OrderModel):
        """ Delivery is ready for pickup so request KitchenService work.

        :param message: DeliveryService metadata response message.
        :param order: Current Order.
        """
        payload = KitchenPayload(metadata=message['metadata'], **order.dict())

        try:
            root = await self.cache.get('KitchenService')

            # Request KitchenService work.
            async with AsyncClient() as client:
                url = f"{root}/v1/kitchen"
                resp = await client.post(url=url, json=payload.dict(),
                                         timeout=config.url_timeout)

            if resp.status_code != 202:
                errmsg = f"Failed KitchenService POST request for URL {url} " \
                         f"- [{resp.status_code}: {resp.json()['detail']}]."
                raise RuntimeError(errmsg)

            data = resp.json()
            order.status = data['status']
            order.kitchen_id = data['kitchen_id']
            order.updated.append(StateUpdateSchema(status=order.status))
            await self._update_order_in_db(order)

        except ConnectTimeout:
            errmsg = f'No connection with KitchenService on URL {url}'
            raise ConnectionError(errmsg)

    # ---------------------------------------------------------
    #
    async def process_response(self, message: dict):
        """ Process response message data.

        Implemented business logic:
          - Every received message state is updated in DB.
          - When status is 'paymentPaid':
              - Trigger DeliveryService work.
          - When status is 'driverAvailable':
              - Trigger KitchenService work.

        :param message: Response message data.
        """
        status = message['status']
        order_id = UUID(message['metadata']['order_id'])

        try:
            # Read specified Order from DB.
            order = await self.repo.read(order_id)

            if not order:
                raise RuntimeError(f'{order_id=} is unknown')

            order.status = status
            order.updated.append(StateUpdateSchema(status=order.status))
            await self._update_order_in_db(order)

            if status == Status.PAID:
                await self._handle_successful_payment(message, order)

            elif status == Status.DRAV:
                await self._handle_delivery_ready(message, order)

        except RuntimeError as why:
            logger.error(f'{why}')

        except ConnectionError as why:
            logger.critical(f'{why}')

        except BaseException as why:
            logger.critical(f'Failed processing response {status=} => {why}')
