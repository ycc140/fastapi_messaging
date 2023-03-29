# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-23 19:52:08
     $Rev: 36
"""

# BUILTIN modules
from typing import List

# Third party modules
from loguru import logger
from httpx import AsyncClient, ConnectTimeout

# local modules
from ..config.setup import config
from ..repository.url_cache import UrlCache
from ..tools.rabbit_client import AbstractRobustConnection
from ..web.api.schemas import ResourceSchema, HealthSchema
from ..repository.order_data_adapter import OrdersRepository

# Constants
URLS = {'PaymentService', 'KitchenService',
        'DeliveryService', 'CustomerService'}
""" Used internal MicroService(s). """


# -----------------------------------------------------------------------------
#
class HealthManager:
    """ This class handles health status reporting on used resources. """

    # ---------------------------------------------------------
    #
    def __init__(self, connection: AbstractRobustConnection,
                 cache: UrlCache, repository: OrdersRepository):
        """ Class initializer.

        :param cache: Redis URL cache.
        :param repository: Data layer handler object.
        :param connection: RabbitMQ's connection object.
        """
        self.cache = cache
        self.repo = repository
        self.connection = connection

    # ---------------------------------------------------------
    #
    async def _get_mongo_status(self) -> List[ResourceSchema]:
        """ Return MongoDb connection status.

        :return: MongoDb connection status.
        """

        try:
            status = True
            await self.repo.connection_info()

        except BaseException as why:
            logger.critical(f'MongoDB: {why}')
            status = False

        return [ResourceSchema(name='MongoDb', status=status)]

    # ---------------------------------------------------------
    #
    async def _get_rabbit_status(self) -> List[ResourceSchema]:
        """ Return RabbitMQ connection status.

        :return: RabbitMQ connection status.
        """

        try:
            status = not self.connection.is_closed

        except BaseException as why:
            logger.critical(f'RabbitMQ: {why}')
            status = False

        return [ResourceSchema(name='RabbitMQ', status=status)]

    # ---------------------------------------------------------
    #
    async def _get_service_status(self) -> List[ResourceSchema]:
        """ Return RabbitMQ connection status.

        :return: Service connection status.
        """
        result = []

        async with AsyncClient() as client:
            for service in URLS:
                try:
                    root = await self.cache.get(service)
                    url = f'{root}/health'
                    status = False

                    # Request used Microservice health status.
                    response = await client.get(url=url, timeout=(1.0, 5.0))

                    if response.status_code == 200:
                        status = response.json()['status']

                except ConnectTimeout:
                    logger.critical(f'No connection with {service} on URL {url}')

                result.append(ResourceSchema(name=service, status=status))

        return result

    # ---------------------------------------------------------
    #
    async def get_status(self) -> HealthSchema:
        """ Return Health status for used resources.

        :return: Service health status.
        """
        resource_items = []
        resource_items += await self._get_mongo_status()
        resource_items += await self._get_rabbit_status()
        resource_items += await self._get_service_status()
        total_status = all(key.status for key in resource_items)

        return HealthSchema(status=total_status,
                            version=config.version,
                            name=config.service_name,
                            resources=resource_items)
