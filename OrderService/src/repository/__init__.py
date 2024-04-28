# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-28 15:32:32
     $Rev: 10
"""

# Third party modules
from fastapi import Depends

# Local modules
from .order_db_adapter import OrderDbAdapter
from .mongo_repository import MongoRepository
from .db import Engine, AsyncIOMotorClientSession


# ---------------------------------------------------------
#
async def get_order_api_repository(
        session: AsyncIOMotorClientSession = Depends(Engine.get_async_session)
) -> OrderDbAdapter:
    """ Return an Order DB adapter object with an active session.

    This call is used by API endpoints where Depends Dependency
    Injections are used.

    :param session: Active database session.
    :return: An Order DB adapter object with an active session.
    """
    return OrderDbAdapter(MongoRepository(session))


# ---------------------------------------------------------
#
async def get_order_response_repository() -> OrderDbAdapter:
    """ Return an Order DB adapter object with an active session.

    This call is used for Payment response messages.

    :return: An Order DB adapter object with an active session.
    """
    session = await Engine.client.start_session()
    return OrderDbAdapter(MongoRepository(session))
