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

# BUILTIN modules
from uuid import UUID
from typing import List

# Third party modules
import ujson
from pymongo import DESCENDING
from redis.asyncio import from_url

# Local modules
from ..core.setup import config
from .db import AsyncIOMotorClientSession
from .models import OrderModel, OrderUpdateModel, dict_of

# Constants
EXPIRE = 60 * 30
""" Cached Order objects expire after 30 minutes. """


# -----------------------------------------------------------------------------
#
class MongoRepository:
    """ This class implements the IRepository abstraction using MongoDB.

    The Order object is cached in Redis. This is handled by the read, update
    and delete methods.

    :ivar session: MongoDb database async client session.
    :type session: motor.motor_asyncio.AsyncIOMotorClientSession
    :ivar cache: Redis client.
    :type cache: redis.asyncio.Redis
    """
    cache = from_url(config.redis_url)

    # ---------------------------------------------------------
    #
    def __init__(self, session: AsyncIOMotorClientSession):
        """ Implicit constructor.

        :param session: MongoDb database async client session.
        """
        self.session = session

    # ---------------------------------------------------------
    #
    async def _read(self, key: UUID) -> OrderModel:
        """ Read Order for a matching index key from DB collection api_db.orders.

        :param key: Index key.
        :return: Found Order.
        """
        response = await self.session.client.api_db.orders.find_one({"_id": str(key)})

        return OrderModel.from_mongo(response) if response else None

    # ---------------------------------------------------------
    #
    async def _update(self, payload: OrderModel) -> bool:
        """ Update Order in DB collection api_db.orders.

        :param payload: Updated Order payload.
        :return: DB update result.
        """
        base = OrderUpdateModel(**payload.model_dump()).to_mongo()
        response = await self.session.client.api_db.orders.update_one({"_id": str(payload.id)},
                                                                      {"$set": {**base}})

        return response.raw_result['updatedExisting']

    # ---------------------------------------------------------
    #
    async def create(self, payload: OrderModel) -> bool:
        """ Create Order in DB collection api_db.orders.

        :param payload: New Order payload.
        :return: DB create response.
        """
        response = await self.session.client.api_db.orders.insert_one(payload.to_mongo())

        return response.acknowledged

    # ---------------------------------------------------------
    #
    async def read_all(self) -> List[OrderModel]:
        """ Read all existing Orders in DB collection api_db.orders.

        Sorted on creation timestamp in descending order.

        :return: List of found Orders.
        """
        result = []

        async for item in self.session.client.api_db.orders.find({}).sort('created', DESCENDING):
            result.append(OrderModel.from_mongo(item))

        return result

    # ---------------------------------------------------------
    #
    async def read(self, key: UUID) -> OrderModel:
        """ Read Order for a matching index key from the cache.

        If it does not exist there, read it from a DB collection
        api_db.orders and update the cache.

        :param key: Index key.
        :return: Found Order.
        """
        value = await self.cache.get(str(key))

        if not value:
            payload = await self._read(key)

            if not payload:
                return None

            value = ujson.dumps(dict_of(payload))
            await self.cache.set(str(key), value, ex=EXPIRE)

        return OrderModel(**ujson.loads(value))

    # ---------------------------------------------------------
    #
    async def update(self, payload: OrderModel) -> bool:
        """ Update Order in DB collection api_db.orders and in the cache.

        :param payload: Updated Order payload.
        :return: DB update result.
        """
        response = await self._update(payload)

        if response:
            value = ujson.dumps(dict_of(payload))
            await self.cache.set(str(payload.id), value, ex=EXPIRE)

        return response

    # ---------------------------------------------------------
    #
    async def delete(self, key: UUID) -> bool:
        """
        Delete Order for a matching index key from a DB collection
        api_db.orders and the cache.

        :param key: Index key.
        :return: DB delete result.
        """
        response = await self.session.client.api_db.orders.delete_one({"_id": str(key)})

        if response.deleted_count == 1:
            await self.cache.delete(str(key))

        return response.deleted_count > 0
