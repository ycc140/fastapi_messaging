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

# Third party modules
from loguru import logger
from ..core.setup import config
from ..tools.rabbit_client import RabbitClient


# ------------------------------------------------------------------------
#
class UnitOfWork:
    """ An async context manager class that publish RabbitMQ messages.

    :ivar broker: The order broker object.
    :type broker: `RabbitClient`
    """

    # ---------------------------------------------------------
    #
    def __init__(self):
        self.broker = RabbitClient(config.rabbit_url)

    # ---------------------------------------------------------
    #
    async def __aenter__(self):
        logger.debug('Establishing RabbitMQ connection...')
        await self.broker.start()
        return self

    # ---------------------------------------------------------
    #
    async def __aexit__(self, exc_type, exc_val, traceback):
        if self.broker.is_connected:
            logger.debug('Disconnecting from RabbitMQ...')
            await self.broker.stop()

    # ---------------------------------------------------------
    #
    async def publish(self, queue: str, message: dict):
        """ Publish a message on specified RabbitMQ queue asynchronously.

        :param queue: Publishing queue.
        :param message: Message to be published.
        """
        await self.broker.publish_message(queue, message)

    # ---------------------------------------------------------
    #
    @property
    def is_connected(self) -> bool:
        """ Return connection status. """
        return self.broker.is_connected
