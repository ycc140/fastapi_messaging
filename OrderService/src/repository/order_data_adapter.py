# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-24 19:33:51
     $Rev: 72
"""

# BUILTIN modules
from uuid import UUID
from typing import List

# Local modules
from .models import OrderModel
from .interface import IRepository
from .mongo_repository import MongoRepository


# ------------------------------------------------------------------------
#
class OrdersRepository:
    """ This class defines the OrderService data layer adapter (the CRUD operations).

    It is implemented using the Repository pattern and is using the Dependency
    Inversion Principle.

    :ivar repository: Current repository instance
    :type repository: `IRepository`
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: IRepository):
        """ The class constructor.

        :param repository: Repository instance to use.
        """
        self.repository = repository

    # ---------------------------------------------------------
    #
    async def create(self, payload: OrderModel) -> bool:
        """ Create Order in DB collection api_db.orders.

        :param payload: New Order payload.
        :return: DB create response.
        """
        return await self.repository.create(payload)

    # ---------------------------------------------------------
    #
    async def read_all(self) -> List[OrderModel]:
        """ Read all existing Orders in DB collection api_db.orders.

        Sorted on creation timestamp in descending order.

        :return: List of found Orders.
        """
        return await self.repository.read_all()

    # ---------------------------------------------------------
    #
    async def read(self, key: UUID) -> OrderModel:
        """ Read Order for a matching index key from the cache.

        If it does not exist there, read it from a DB collection
        api_db.orders and update the cache.

        :param key: Index key.
        :return: Found Order.
        """
        return await self.repository.read(key)

    # ---------------------------------------------------------
    #
    async def update(self, payload: OrderModel) -> bool:
        """ Update Order in DB collection api_db.orders and in the cache.

        :param payload: Updated Order payload.
        :return: DB update result.
        """
        return await self.repository.update(payload)

    # ---------------------------------------------------------
    #
    async def delete(self, key: UUID) -> bool:
        """
        Delete Order for a matching index key from a DB collection
        api_db.orders and the cache.

        :param key: Index key.
        :return: DB delete result.
        """
        return await self.repository.delete(key)


orders_repository = OrdersRepository(MongoRepository())
""" Repository injected with MongoDB implementation. """
