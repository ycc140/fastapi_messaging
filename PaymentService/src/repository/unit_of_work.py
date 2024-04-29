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
from .mongo_repository import MongoRepository
from .payment_db_adapter import PaymentDbAdapter


# ------------------------------------------------------------------------
#
class UnitOfRepositoryWork:
    """ An async context manager class that handles Payment Repository work.

    :ivar session: The DB session object.
    :type session: AsyncIOMotorClientSession
    """

    # ---------------------------------------------------------
    #
    def __init__(self):
        self.session = None

    # ---------------------------------------------------------
    #
    async def __aenter__(self) -> PaymentDbAdapter:
        """ Start a DB session and return a Payment repository.

        :return: Order repository with an active DB session.
        """
        logger.info('Establishing MongoDB session...')
        self.session = await Engine.client.start_session()
        return PaymentDbAdapter(MongoRepository(self.session))

    # ---------------------------------------------------------
    #
    async def __aexit__(self, exc_type, exc_val, traceback):
        """ End the DB session. """
        logger.info('Ending MongoDB session...')
        await self.session.end_session()
