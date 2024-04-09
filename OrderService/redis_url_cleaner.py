#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-09 05:39:25
     $Rev: 4
"""

# BUILTIN modules
import asyncio

# Third party modules
from redis.asyncio import from_url

# Local modules
from src.core.setup import config

# Constants
URLS = {'PaymentService',
        'KitchenService',
        'DeliveryService',
        'CustomerService'}
""" Service dependencies."""


# ---------------------------------------------------------
#
async def cleaner():
    """ Clean the redis URL cache. """
    client = from_url(config.redis_url)

    for key in URLS:
        data = await client.delete(key)
        print(f'deleting: {key}: {data}...')

    await client.aclose()


# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(cleaner())
