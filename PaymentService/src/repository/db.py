# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-09 05:37:36
     $Rev: 3
"""

# Third party modules
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Local program modules
from ..core.setup import config


# ---------------------------------------------------------
#
class Engine:
    """ MongoDb database async engine class.

    :ivar db: AsyncIOMotorDatabase class instance.
    :type db: AsyncIOMotorDatabase
    :ivar connection: AsyncIOMotorClient class instance.
    :type connection: AsyncIOMotorClient
    """

    db: AsyncIOMotorDatabase = None
    connection: AsyncIOMotorClient = None

    # ---------------------------------------------------------
    #
    @classmethod
    async def create_db_connection(cls):
        """ Initialize connection to MongoDb and default database.

        Setting server connection timeout to 5 (default is 30) seconds.
        """
        cls.connection = AsyncIOMotorClient(config.mongo_url,
                                            uuidRepresentation='standard',
                                            serverSelectionTimeoutMS=5000)
        cls.db = cls.connection.api_db

    # ---------------------------------------------------------
    #
    @classmethod
    async def close_db_connection(cls):
        """ Close DB connection. """
        if cls.connection:
            cls.connection.close()

    # ---------------------------------------------------------
    #
    @classmethod
    async def is_db_connected(cls) -> bool:
        """ Return DB connection status. """
        return bool(cls.connection.server_info())
