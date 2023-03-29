#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-25 00:01:55
     $Rev: 41
"""

# BUILTIN modules
import asyncio
import contextlib

# Local modules
from src.config.setup import config
from src.tools.rabbit_client import RabbitClient

# Constants
SERVICE = 'TestService'


# ---------------------------------------------------------
#
async def process_incoming_message(message: dict):
    print(f'Received: {message}')


# ---------------------------------------------------------
#
async def receiver():
    print('Started RabbitMQ message queue subscription...')
    client = RabbitClient(config.rabbit_url, SERVICE, process_incoming_message)
    connection = await asyncio.create_task(client.consume())

    try:
        # Wait until terminate
        await asyncio.Future()

    finally:
        await connection.close()


# ---------------------------------------------------------

if __name__ == "__main__":

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(receiver())
