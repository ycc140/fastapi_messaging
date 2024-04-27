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
import asyncio

# Local modules
from ..repository.interface import IRepository
from ..business.response_handler import OrderPaymentResponseLogic


# ------------------------------------------------------------------------
#
class OrderEventAdapter:
    """ This class is the Order primary adapter PaymentResponse implementation.

    :ivar repo: The order repository object.
    :type repo: `IRepository`
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: IRepository):
        """ The class initializer.

        :param repository: The order repository object.
        """
        self.repo = repository

    # ---------------------------------------------------------
    #
    async def process_payment_response(self, message: dict):
        """ Process payment response message data.

        Implemented business logic:
          - Every received message state is updated in DB.
          - When status is 'paymentPaid':
              - Trigger DeliveryService work.
          - When status is 'driverAvailable':
              - Trigger KitchenService work.

        :param message: Response message data.
        """
        worker = OrderPaymentResponseLogic(repository=self.repo)
        await asyncio.create_task(worker.process_response(message))
