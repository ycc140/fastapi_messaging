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

# Local modules
from .models import PaymentModel
from .interface import IRepository


# ------------------------------------------------------------------------
#
class PaymentDbAdapter:
    """
    This class implements the PaymentService secondary adapter database
    implementation (the CRUD operations).

    It is implemented using the Repository pattern and is using
    the Dependency Inversion Principle.

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
    async def create(self, payload: PaymentModel) -> bool:
        """ Create Payment in DB collection api_db.payments.

        :param payload: New Payment payload.
        :return: DB create response.
        """
        return await self.repository.create(payload)

    # ---------------------------------------------------------
    #
    async def read(self, key: UUID) -> PaymentModel:
        """ Read Payment for matching index key from DB collection api_db.payments.

        :param key: Index key.
        :return: Found Payment.
        """
        return await self.repository.read(key)

    # ---------------------------------------------------------
    #
    async def update(self, payload: PaymentModel) -> bool:
        """ Update Payment in a DB collection api_db.payments.

        :param payload: Updated Payment payload.
        :return: DB update result.
        """
        return await self.repository.update(payload)
