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
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClientSession

# From local modules.
from .db import Engine
from .order_db_adapter import OrderDbAdapter
from .mongo_repository import MongoRepository


# ------------------------------------------------------------------------
#
class UnitOfRepositoryWork:
    """ An async context manager class that handles Order Repository work.

    :ivar session: The DB session object.
    :type session: AsyncIOMotorClientSession
    """

    # ---------------------------------------------------------
    #
    def __init__(self):
        self.session = None

    # ---------------------------------------------------------
    #
    async def __aenter__(self) -> OrderDbAdapter:
        """ Start a DB session and return an Order repository.

        :return: Order repository with an active DB session.
        """
        logger.debug('Establishing MongoDB session...')
        self.session = await Engine.client.start_session()
        return OrderDbAdapter(MongoRepository(self.session))

    # ---------------------------------------------------------
    #
    async def __aexit__(self, exc_type, exc_val, traceback):
        """ End the DB session. """
        logger.debug('Ending MongoDB session...')
        await self.session.end_session()
