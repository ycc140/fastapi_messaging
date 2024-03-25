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

# Local modules
from .db import Engine
from .models import PaymentModel, PaymentUpdateModel


# -----------------------------------------------------------------------------
#
class MongoRepository:
    """
    This class implements the IRepository abstraction using MongoDB.


    @ivar engine: MongoDb database async engine instance
    """
    engine = Engine

    # ---------------------------------------------------------
    #
    async def create(self, payload: PaymentModel) -> bool:
        """ Create Payment in DB collection api_db.payments.

        :param payload: New Payment payload.
        :return: DB create response.
        """
        response = await self.engine.db.payments.insert_one(payload.to_mongo())

        return response.acknowledged

    # ---------------------------------------------------------
    #
    async def read(self, key: UUID) -> PaymentModel:
        """ Read Payment for matching index key from DB collection api_db.payments.

        :param key: Index key.
        :return: Found Payment.
        """
        response = await self.engine.db.payments.find_one({"_id": str(key)})

        return PaymentModel.from_mongo(response)

    # ---------------------------------------------------------
    #
    async def update(self, payload: PaymentModel) -> bool:
        """ Update Payment in a DB collection api_db.payments.

        :param payload: Updated Order payload.
        :return: DB update result.
        """
        base = PaymentUpdateModel(**payload.model_dump()).to_mongo()
        response = await self.engine.db.payments.update_one({"_id": str(payload.id)},
                                                            {"$set": {**base}})

        return response.raw_result['updatedExisting']
