# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-29 09:43:22
     $Rev: 14
"""

# Third party modules
from motor.motor_asyncio import AsyncIOMotorClient

# Local program modules
from ..core.setup import config


# ---------------------------------------------------------
#
class Engine:
    """ MongoDb database async engine class.

    :ivar client: MongoDB motor async client object.
    :type client: AsyncIOMotorClient
    """
    client: AsyncIOMotorClient = None

    # ---------------------------------------------------------
    #
    @classmethod
    async def create_db_connection(cls):
        """ Initialize connection to MongoDb and default database.

        Setting server connection timeout to 5 (default is 30) seconds.
        """
        cls.client = AsyncIOMotorClient(config.mongo_url,
                                        uuidRepresentation='standard',
                                        serverSelectionTimeoutMS=5000)

    # ---------------------------------------------------------
    #
    @classmethod
    async def close_db_connection(cls):
        """ Close DB connection. """
        if cls.client:
            cls.client.close()

    # ---------------------------------------------------------
    #
    @classmethod
    async def is_db_connected(cls) -> bool:
        """ Return DB connection status. """
        return bool(cls.client.server_info())
