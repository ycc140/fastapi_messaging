#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-22 20:51:42
     $Rev: 69
"""

# BUILTIN modules
import asyncio

# Local modules
from src.config.setup import config
from src.tools.rabbit_client import RabbitClient

# Constants
SERVICE = 'TestService'
""" Service name. """
CLIENT = RabbitClient(config.rabbit_url)
""" RabbitMQ client instance. """


# ---------------------------------------------------------
#
async def sender():
    """ Send ten messages. """
    await CLIENT.start()

    for idx in range(1, 11):
        msg = {"title": f"message no {idx}"}
        await CLIENT.publish_message(SERVICE, msg)
        print(f'Sent message: {msg}')

    await CLIENT.stop()


# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(sender())
