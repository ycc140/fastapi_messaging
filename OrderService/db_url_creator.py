# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-24 23:50:19
     $Rev: 40
"""

# BUILTIN modules
import asyncio

# Local modules
from src.repository.db import Engine

# Constants
URLS = {'CustomerService': 'http://127.0.0.1:8002',
        'DeliveryService': 'http://127.0.0.1:8003',
        'KitchenService': 'http://127.0.0.1:8004',
        'PaymentService': 'http://127.0.0.1:8001'}


# ---------------------------------------------------------
#
async def creator():
    """ Insert URL in api_db.service_urls collection.

    Drop the collection if it already exists, before the insertion.
    """
    await Engine.connect_to_mongo()

    await Engine.db.service_urls.drop()
    print("Dropped api_db.service_urls collection.")

    response = [{'_id': key, 'url': item} for key, item in URLS.items()]

    await Engine.db.service_urls.insert_many(response)
    result = await Engine.db.service_urls.count_documents({})
    print(result, "MicroService URLs are inserted in api_db.service_urls.")

    await Engine.close_mongo_connection()


# ---------------------------------------------------------

if __name__ == "__main__":

    asyncio.run(creator())
