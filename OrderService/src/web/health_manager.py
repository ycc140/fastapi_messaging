# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-28 15:22:00
     $Rev: 9
"""

# BUILTIN modules
from typing import List
from pathlib import Path
from datetime import date

# Third party modules
import aiofiles
from loguru import logger
from httpx import AsyncClient, ConnectTimeout

# local modules
from ..repository.db import Engine
from ..core.setup import config, SSL_CONTEXT
from ..tools.rabbit_client import RabbitClient
from ..repository.url_cache import UrlServiceCache
from ..web.api.models import HealthResourceModel, HealthResponseModel

# Constants
URLS = {'PaymentService', 'KitchenService',
        'DeliveryService', 'CustomerService'}
""" Used internal MicroService(s). """
CERT_EXPIRE_FILE = (
        Path(__file__).parent.parent.parent / 'certs' / 'expire-date.txt'
)
""" File containing certificate expiry date. """


# -----------------------------------------------------------------------------
#
class HealthManager:
    """ This class handles health status reporting on used resources.

    :ivar rabbit_client: RabbitMQ client.
    :type rabbit_client: `RabbitClient`
    """

    # ---------------------------------------------------------
    #
    def __init__(self, rabbit_client: RabbitClient):
        """ Class initializer.

        :param rabbit_client: RabbitMQ's connection object.
        """
        self.rabbit_client = rabbit_client

    # ---------------------------------------------------------
    #
    @staticmethod
    async def _get_cert_remaining_days() -> int:
        """ Return SSL certificate remaining valid days.

        Will return 0 if the cert expires-date file is missing,
        or an invalid ISO 8601 date format (YYYY-MM-DD) is found.

        :return: Remaining valid certificate days.
        """
        try:
            async with aiofiles.open(CERT_EXPIRE_FILE, mode='r') as cert:
                raw_date = await cert.read()

            remaining_days = date.fromisoformat(raw_date) - date.today()
            return remaining_days.days

        except (EnvironmentError, ValueError):
            return 0

    # ---------------------------------------------------------
    #
    @staticmethod
    def _get_cert_status(remaining_days: int) -> List[HealthResourceModel]:
        """ Return SSL certificate validity status.

        :return: Certificate validity status.
        """
        return [HealthResourceModel(name='Certificate.valid',
                                    status=remaining_days > 0)]

    # ---------------------------------------------------------
    #
    @staticmethod
    async def _get_repo_status() -> List[HealthResourceModel]:
        """ Return MongoDb connection status.

        :return: MongoDb connection status.
        """
        try:
            status = await Engine.is_db_connected()

        except BaseException as why:
            logger.critical(f'MongoDB: {why}')
            status = False

        return [HealthResourceModel(name='MongoDb', status=status)]

    # ---------------------------------------------------------
    #
    async def _get_broker_status(self) -> List[HealthResourceModel]:
        """ Return RabbitMQ connection status.

        :return: RabbitMQ connection status.
        """
        status = self.rabbit_client.is_connected
        return [HealthResourceModel(name='RabbitMQ', status=status)]

    # ---------------------------------------------------------
    #
    @staticmethod
    async def _get_service_status() -> List[HealthResourceModel]:
        """ Return RabbitMQ connection status.

        :return: Service connection status.
        """
        result = []
        cache = UrlServiceCache(config.redis_url)

        try:
            async with AsyncClient(verify=SSL_CONTEXT,
                                   timeout=(1.0, 5.0)) as client:
                for service in URLS:
                    try:
                        root = await cache.get(service)
                        url = f'{root}/health'
                        status = False

                        # Request used Microservice health status.
                        response = await client.get(url=url)

                        if response.status_code == 200:
                            status = response.json()['status']

                    except ConnectTimeout:
                        logger.critical(f'No connection with '
                                        f'{service} on URL {url}')

                    result.append(HealthResourceModel(name=service, status=status))

        finally:
            await cache.close()

        return result

    # ---------------------------------------------------------
    #
    async def get_status(self) -> HealthResponseModel:
        """ Return Health status for used resources.

        :return: Service health status.
        """
        resource_items = []
        days = await self._get_cert_remaining_days()
        resource_items += self._get_cert_status(days)
        resource_items += await self._get_repo_status()
        resource_items += await self._get_broker_status()
        resource_items += await self._get_service_status()
        total_status = all(key.status for key in resource_items)

        return HealthResponseModel(status=total_status,
                                   version=config.version,
                                   name=config.service_name,
                                   resources=resource_items,
                                   cert_remaining_days=days)
