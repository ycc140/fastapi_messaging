# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-24 19:33:51
     $Rev: 72
"""

# BUILTIN modules
import asyncio
from typing import Callable, Optional, Any

# Third party modules
import ujson as json
from aio_pika.exceptions import AMQPConnectionError
from aio_pika import (DeliveryMode, connect_robust,
                      RobustConnection, IncomingMessage, Message)


# -----------------------------------------------------------------------------
#
class RabbitClient:
    """ This class implements RabbitMQ Publish and Subscribe async handling.

    The RabbitMQ queue mechanism is used so that we can take advantage of
    good horizontal message scaling when needed.

    :ivar channel: RabbitMQ's connection channel object instance.
    :type channel: ``aio_pika.AbstractChannel``
    :ivar rabbit_url: RabbitMQ's connection URL.
    :ivar service_name: Name of message subscription queue.
    :ivar message_handler: Received message callback method.
    :ivar connection: RabbitMQ's connection object instance.
    :type connection: ``aio_pika.AbstractRobustConnection``
    """

    # ---------------------------------------------------------
    #
    def __init__(self, rabbit_url: str, service: Optional[str] = None,
                 incoming_message_handler: Optional[Callable] = None):
        """ The class initializer.

        :param rabbit_url: RabbitMQ's connection URL.
        :param service: Name of message subscription queue.
        :param incoming_message_handler: Received message callback method.
        """
        self.channel = None
        self.connection = None
        self.rabbit_url = rabbit_url
        self.service_name = service
        self.message_handler = incoming_message_handler

    # ---------------------------------------------------------
    #
    async def _process_incoming_message(self, message: IncomingMessage):
        """ Processing an incoming message from RabbitMQ.

        :param message: The received message.
        """
        if body := message.body:
            await self.message_handler(json.loads(body))

        await message.ack()

    # ---------------------------------------------------------
    #
    def _on_connection_closed(self, _: Any, __: AMQPConnectionError):
        """ Handle unexpectedly closed connection events.

        :param _: Not used.
        :param __: Not used.
        """
        self.connection_lost = None

    # ---------------------------------------------------------
    #
    async def _on_connection_reconnected(self, connection: RobustConnection):
        """ Send a LinkUp message when the connection is reconnected.

        :param connection: RabbitMQ's robust connection instance.
        """
        self.connection = connection

    # ---------------------------------------------------------
    #
    async def _initiate_communication(self):
        """ Establish communication with RabbitMQ (connection + channel).

        Send a LinkUp message when communication is established.
        """
        loop = asyncio.get_running_loop()

        # Create a RabbitMQ connection that automatically reconnects.
        self.connection = await connect_robust(loop=loop, url=self.rabbit_url)
        self.connection.reconnect_callbacks.add(self._on_connection_reconnected)
        self.connection.close_callbacks.add(self._on_connection_closed)

        # Create a publishing, or subscription channel.
        self.channel = await self.connection.channel()

        # To make sure the load is evenly distributed between the workers.
        await self.channel.set_qos(1)

    # ---------------------------------------------------------
    #
    async def start_subscription(self):
        """ Setup message listener with the current running asyncio loop. """

        # Creating a receive queue.
        queue = await self.channel.declare_queue(name=self.service_name, durable=True)

        # Start consuming existing and future messages.
        await queue.consume(self._process_incoming_message, no_ack=False)

    # ---------------------------------------------------------
    #
    async def publish_message(self, queue: str, message: dict):
        """ Publish a message on specified RabbitMQ queue asynchronously.

        :param queue: Publishing queue.
        :param message: Message to be published.
        """

        # Create a message and publish it.
        message_body = Message(
            content_type='application/json',
            delivery_mode=DeliveryMode.PERSISTENT,
            body=json.dumps(message, ensure_ascii=False).encode())
        await self.channel.default_exchange.publish(
            routing_key=queue, message=message_body)

    # ---------------------------------------------------------
    #
    @property
    def is_connected(self) -> bool:
        """ Return connection status. """
        return False if self.connection is None else not self.connection.is_closed

    # ---------------------------------------------------------
    #
    async def start(self):
        """ Start the used resources in a controlled way. """
        await self._initiate_communication()

    # ---------------------------------------------------------
    #
    async def stop(self):
        """ Stop the used resources in a controlled way. """
        if self.connection:
            await self.connection.close()
