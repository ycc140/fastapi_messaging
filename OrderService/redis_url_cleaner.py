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

# Third party modules
from aioredis import from_url

# Local modules
from src.config.setup import config

# Constants
URLS = {'PaymentService': 'http://127.0.0.1:8001',
        'KitchenService': 'http://127.0.0.1:8004',
        'DeliveryService': 'http://127.0.0.1:8003',
        'CustomerService': 'http://127.0.0.1:8002'}


# ---------------------------------------------------------
#
async def cleaner():
    client = from_url(config.redis_url)

    for key in URLS:
        await client.delete(key)


# ---------------------------------------------------------

if __name__ == "__main__":

    asyncio.run(cleaner())
