# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-27 21:26:58
     $Rev: 8
"""

# Third party modules
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession

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

    # ---------------------------------------------------------
    #
    @classmethod
    async def get_async_session(cls) -> AsyncIOMotorClientSession:
        """ Return an active database session object from the pool.

        Note that this is a DB session generator.

        Returns:
            An active DB session.
        """
        async with await cls.client.start_session() as session:
            yield session
