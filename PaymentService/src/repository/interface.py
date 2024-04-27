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
from typing import Protocol

# Local modules
from .models import PaymentModel


# -----------------------------------------------------------------------------
#
class IRepository(Protocol):
    """ Payment DB Interface class. """

    async def create(self, payload: PaymentModel) -> bool:
        """ Create Payment.

        :param payload: New Payment payload.
        :return: DB create response.
        """

    async def read(self, key: UUID) -> PaymentModel:
        """ Read Payment for matching index key.

        :param key: Index key.
        :return: Found Payment.
        """

    async def update(self, payload: PaymentModel) -> bool:
        """ Update Payment.

        :param payload: Updated Order payload.
        :return: DB update result.
        """
