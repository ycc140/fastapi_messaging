# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-24 23:18:27
     $Rev: 38
"""

# Third party modules
from aioredis import from_url

# Local modules
from .db import Engine

# Constants
EXPIRE = 60*60*24
""" Redis keys expire after 24h. """


# ------------------------------------------------------------------------
#
class UrlCache:
    """ This class handles Redis URL cache.

    Is automatically populated from MongoDB api_db.service_urls collection.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, url: str):
        """  The class initializer.

        :param url: Redis connection URL.
        """
        self.client = from_url(url)

    # ---------------------------------------------------------
    #
    async def get(self, key: str) -> str:
        """ Get MicroService URL from Redis.

        Populate from MongoDB api_db.service_urls collection if needed.
        All URL Keys expire after 24h in the cache.

        :param key: MicroService name.
        :return: MicroService URL.
        """
        value = await self.client.get(key)

        if not value:
            value = await Engine.db.service_urls.find_one({"_id": key})
            await self.client.set(key, value['url'], ex=EXPIRE)

        return value.decode() if isinstance(value, bytes) else value['url']
