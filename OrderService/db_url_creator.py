# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-12-20 13:46:05
     $Rev: 16
"""

# BUILTIN modules
import asyncio

# Local modules
from src.repository.db import Engine

# Constants
URLS = {'KitchenService': 'http://127.0.0.1:8004',
        'PaymentService': 'https://127.0.0.1:8001',
        'DeliveryService': 'http://127.0.0.1:8003',
        'CustomerService': 'http://127.0.0.1:8002'}
""" Service dependencies."""


# ---------------------------------------------------------
#
async def creator():
    """ Insert URL in api_db.service_urls collection.

    Drop the collection if it already exists before the insertion.
    """
    await Engine.create_db_connection()

    await Engine.client.service_urls.drop()
    print("Dropped api_db.service_urls collection.")

    response = [{'_id': key, 'url': item} for key, item in URLS.items()]

    await Engine.client.service_urls.insert_many(response)
    result = await Engine.client.service_urls.count_documents({})
    print(result, "MicroService URLs are inserted in api_db.service_urls.")

    await Engine.close_db_connection()


# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(creator())
