# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-09 06:17:52
     $Rev: 5
"""

# BUILTIN modules
from uuid import UUID
from typing import Protocol, List

# Local modules
from .models import OrderModel


# -----------------------------------------------------------------------------
#
class IRepository(Protocol):
    """ DB Interface class. """

    async def create(self, payload: OrderModel) -> bool:
        """ Create Payment.

        :param payload: New Payment payload.
        :return: DB create response.
        """
        ...

    async def read_all(self) -> List[OrderModel]:
        """ Read all existing Orders.

        Sorted on creation timestamp in descending order.

        :return: List of found Orders.
        """
        ...

    async def read(self, key: UUID) -> OrderModel:
        """ Read Order for a matching index key.

        :param key: Index key.
        :return: Found Order.
        """
        ...

    async def update(self, payload: OrderModel) -> bool:
        """ Update Order.

        :param payload: Updated Order payload.
        :return: DB update result.
        """
        ...

    async def delete(self, key: UUID) -> bool:
        """
        Delete Order for a matching index key from a DB collection
        api_db.orders and the cache.

        :param key: Index key.
        :return: DB delete result.
        """
        ...
