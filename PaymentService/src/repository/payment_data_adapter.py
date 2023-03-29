# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-23 19:52:08
     $Rev: 36
"""

# Third party modules
from pydantic import UUID4

# Local modules
from .db import Engine
from .models import (PaymentModel, PaymentUpdateModel)


# ------------------------------------------------------------------------
#
class PaymentsRepository:
    """
    This class implements the PaymentService data layer adapter (the CRUD operations).
    """

    # ---------------------------------------------------------
    #
    @staticmethod
    async def connection_info() -> dict:
        """ Return DB connection information.

        :return: DB connection information.
        """
        return await Engine.connection.server_info()

    # ---------------------------------------------------------
    #
    @staticmethod
    async def create(payload: PaymentModel) -> bool:
        """ Create Payment in DB collection api_db.payments.

        :param payload: New Payment payload.
        :return: DB create result.
        """
        response = await Engine.db.payments.insert_one(payload.to_mongo())

        return response.acknowledged

    # ---------------------------------------------------------
    #
    @staticmethod
    async def read(key: UUID4) -> PaymentModel:
        """ Read Payment for matching index key from DB collection api_db.payments.

        :param key: Index key.
        :return: Found Payment.
        """

        response = await Engine.db.payments.find_one({"_id": str(key)})

        return PaymentModel.from_mongo(response)

    # ---------------------------------------------------------
    #
    @staticmethod
    async def update(payload: PaymentModel) -> bool:
        """ Update Payment in DB collection api_db.payments.

        :param payload: Updated Order payload.
        :return: DB update result.
        """

        base = PaymentUpdateModel(**payload.dict()).to_mongo()
        response = await Engine.db.payments.update_one({"_id": str(payload.id)},
                                                       {"$set": {**base}})

        return response.raw_result['updatedExisting']
