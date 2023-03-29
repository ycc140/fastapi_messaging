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

# Local modules
from src.config.setup import config
from src.tools.rabbit_client import RabbitClient

# Constants
SERVICE = 'TestService'
CLIENT = RabbitClient(config.rabbit_url)


# ---------------------------------------------------------
#
async def sender():

    for idx in range(1, 11):
        msg = {"title": f"message no {idx}"}
        await CLIENT.send_message(msg, SERVICE)
        print(f'Sent message: {msg}')


# ---------------------------------------------------------

if __name__ == "__main__":

    asyncio.run(sender())
