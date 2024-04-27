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
from fastapi import Depends

# Local modules
from .mongo_repository import MongoRepository
from .payment_db_adapter import PaymentDbAdapter
from .db import Engine, AsyncIOMotorClientSession


# ---------------------------------------------------------
#
async def get_payment_repository(
        session: AsyncIOMotorClientSession = Depends(Engine.get_async_session)
) -> PaymentDbAdapter:
    """ Return Item CRUD operation instance with an active DB session.

    :param session: Active database session.
    :return: Item CRUD object with an active DB session.
    """
    return PaymentDbAdapter(MongoRepository(session))
