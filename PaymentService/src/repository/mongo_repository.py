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

# BUILTIN modules
from uuid import UUID

# Third party modules
from motor.motor_asyncio import AsyncIOMotorClientSession

# Local modules
from .models import PaymentModel, PaymentUpdateModel


# -----------------------------------------------------------------------------
#
class MongoRepository:
    """
    This class implements the IRepository abstraction using MongoDB.


    :ivar session: MongoDb database async client session.
    :type session: motor.motor_asyncio.AsyncIOMotorClientSession
    """

    # ---------------------------------------------------------
    #
    def __init__(self, session: AsyncIOMotorClientSession):
        """ Implicit constructor.

        :param session: MongoDb database async client session.
        """
        self.session = session

    # ---------------------------------------------------------
    #
    async def create(self, payload: PaymentModel) -> bool:
        """ Create Payment in DB collection api_db.payments.

        :param payload: New Payment payload.
        :return: DB create response.
        """
        response = await self.session.client.api_db.payments.insert_one(payload.to_mongo())

        return response.acknowledged

    # ---------------------------------------------------------
    #
    async def read(self, key: UUID) -> PaymentModel:
        """ Read Payment for matching index key from DB collection api_db.payments.

        :param key: Index key.
        :return: Found Payment.
        """
        response = await self.session.client.api_db.payments.find_one({"_id": str(key)})

        return PaymentModel.from_mongo(response)

    # ---------------------------------------------------------
    #
    async def update(self, payload: PaymentModel) -> bool:
        """ Update Payment in a DB collection api_db.payments.

        :param payload: Updated Order payload.
        :return: DB update result.
        """
        base = PaymentUpdateModel(**payload.model_dump()).to_mongo()
        response = await self.session.client.api_db.payments.update_one({"_id": str(payload.id)},
                                                                        {"$set": {**base}})

        return response.raw_result['updatedExisting']
