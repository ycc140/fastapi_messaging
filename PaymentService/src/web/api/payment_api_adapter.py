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

# Local modules
from ...tools.rabbit_client import RabbitClient
from ...repository.interface import IRepository
from ...business.payment_handler import PaymentLogic
from .models import BillingCallback, PaymentPayload


# ------------------------------------------------------------------------
#
class PaymentApiAdapter:
    """ This class is the PaymentService primary adapter API implementation.

    :ivar repo: The order repository object.
    :type repo: `IRepository`
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: IRepository, client: RabbitClient):
        """ The class initializer.

        :param repository: Data layer handler object.
        :param client: RabbitMQ client.
        """
        self.repo = repository
        self.rabbit_client = client

    # ---------------------------------------------------------
    #
    async def process_payment_request(self, payload: PaymentPayload):
        """ Process payment request.

         Implemented logic:
           - Get customer billing data and amount-to-pay from the CustomerService.
           - Send the payment request to the external Credit Card Company.
           - Store payment in DB collection api_db.payments.

        :param payload: Payment request data.
        :raise HTTPException [500]: When processing request failed.
        :raise HTTPException [400]: When HTTP POST response != 201 or 202.
        :raise HTTPException [500]: When connection with CustomerService failed.
        """
        payment = PaymentLogic(self.repo, self.rabbit_client)
        return await payment.process_payment_request(payload)

    # ---------------------------------------------------------
    #
    async def process_reimbursement_request(self, payload: PaymentPayload):
        """ Process reimbursement request.

         Implemented logic:
           - Get customer billing data and amount-to-reimburse from the CustomerService.
           - Send the reimbursement request to the external Credit Card Company.
           - Update payment status in DB collection api_db.payments.

        :param payload: Reimbursement request data.
        :raise HTTPException [500]: When processing request failed.
        :raise HTTPException [400]: When HTTP POST response != 201 or 202.
        :raise HTTPException [500]: When connection with CustomerService failed.
        """
        payment = PaymentLogic(self.repo, self.rabbit_client)
        return await payment.process_reimbursement_request(payload)

    # ---------------------------------------------------------
    #
    async def process_response(self, payload: BillingCallback) -> BillingCallback:
        """ Process payment/reimbursement callback response.

         Implemented logic:
           - Extract payment Order from DB using payload caller_id.
           - Store updated billing data in a DB collection api_db.payments.
           - Send the billing response to the metadata requester using RabbitMQ.

        :param payload: Payment callback response data.
        :return: Received payload.
        :raise HTTPException [404]: When caller_id does not exist in DB.
        """
        payment = PaymentLogic(self.repo, self.rabbit_client)
        return await payment.process_response(payload)
