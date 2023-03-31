# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-31 21:37:40
     $Rev: 54
"""


# BUILTIN modules
import contextlib
from uuid import UUID, uuid4

# Third party modules
from loguru import logger
from fastapi import HTTPException
from httpx import AsyncClient, ConnectError, ConnectTimeout

# Local modules
from ..config.setup import config
from .schemas import PaymentResponse
from ..repository.url_cache import UrlCache
from ..repository.models import PaymentModel
from ..tools.rabbit_client import RabbitClient
from ..repository.payment_data_adapter import PaymentsRepository
from ..web.api.schemas import BillingCallback, BillingPayload, PaymentPayload


# -----------------------------------------------------------------------------
#
class PaymentLogic:
    """
    This class implements the PaymentService business logic layer.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: PaymentsRepository,
                 cache: UrlCache, client: RabbitClient):
        """ The class initializer.

        :param repository: Data layer handler object.
        :param cache: Redis URL cache.
        :param client: RabbitMQ client.
        """
        self.cache = cache
        self.client = client
        self.repo = repository

    # ---------------------------------------------------------
    #
    @staticmethod
    async def _charge_credit_card(payload: BillingPayload) -> UUID:
        """ Simulate doing the Credit Card billing.

        :param payload: Data needed for Billing.
        :return: Credit Card Company transaction ID.
        :raise RuntimeError: when Post response status != 202.
        """

        # Fake the billing work (URL is fake, so it will never connect).
        with contextlib.suppress(ConnectError):
            async with AsyncClient() as client:
                url = "http://fakeCreditCardCompany.com/billings"
                resp = await client.post(url=url, json=payload.dict(),
                                         timeout=config.url_timeout)

            if resp.status_code != 202:
                errmsg = f"Failed sending POST request to Credit Card Company " \
                             f"URL {url} - [{resp.status_code}: {resp.text}]."
                raise RuntimeError(errmsg)

        logger.info(f"Sent Billing request with caller_id '{payload.caller_id}'.")

        # This should be something like: return resp.json()['tracking_id']
        # but since we fake it, we need an id.
        return uuid4()

    # ---------------------------------------------------------
    #
    @staticmethod
    async def _reimburse_credit_card(payload: BillingPayload) -> None:
        """ Simulate doing the Credit Card reimbursement.

        :param payload: Data needed for reimbursement.
        :raise RuntimeError: when Post response status != 202.
        """

        # Fake the reimbursement work (URL is fake, so it will never connect).
        with contextlib.suppress(ConnectError):
            async with AsyncClient() as client:
                url = "http://fakeCreditCardCompany.com/billings/reimburse"
                resp = await client.post(url=url, json=payload.dict(),
                                         timeout=config.url_timeout)

            if resp.status_code != 202:
                errmsg = f"Failed sending POST request to Credit Card Company " \
                             f"URL {url} - [{resp.status_code}: {resp.text}]."
                raise RuntimeError(errmsg)

        logger.info(f"Sent reimbursement request with caller_id '{payload.caller_id}'.")

    # ---------------------------------------------------------
    #
    async def process_payment_request(self, payload: PaymentPayload):
        """ Process payment request.

         Implemented logic:
           - Get customer billing data and amount-to-pay from the CustomerService.
           - Send the payment request to the external Credit Card Company.
           - Store payment in DB collection api_db.payments.

        :param payload: Payment request data.
        :raise HTTPException [500]: when processing request failed.
        :raise HTTPException [400]: when HTTP POST response != 201 or 202.
        :raise HTTPException [500]: when connection with CustomerService failed.
        """
        url = None

        try:
            meta = payload.metadata
            root = await self.cache.get('CustomerService')
            items = [item.dict() for item in payload.items]

            # Get Customer Credit Card information.
            async with AsyncClient() as client:
                url = f"{root}/v1/customers/{meta.customer_id}/billing"
                resp = await client.post(url=url, json=items,
                                         timeout=config.url_timeout)

            if resp.status_code != 201:
                errmsg = f"Failed CustomerService POST request for URL " \
                         f"{url} - [{resp.status_code}: {resp.json()['detail']}]."
                raise RuntimeError(errmsg)

            # Charge the Customer credit card.
            url = "http://fictitious.com/v1/payments/callback"
            billing = BillingPayload(caller_id=meta.order_id,
                                     callback_url=url, **resp.json())
            trans_id = await self._charge_credit_card(billing)

            # Store payment in DB.
            payment = PaymentModel(metadata=meta,
                                   id=meta.order_id,
                                   transaction_id=trans_id)
            await self.repo.create(payment)

        except RuntimeError as why:
            logger.error(f'{why}')
            raise HTTPException(status_code=400, detail=f'{why}')

        except ConnectTimeout:
            errmsg = f'No connection with CustomerService on URL {url}'
            logger.critical(errmsg)
            raise HTTPException(status_code=500, detail=errmsg)

        except BaseException as why:
            logger.critical(f'Failed processing payment request => {why}')
            raise HTTPException(status_code=500, detail=f'{why}')

    # ---------------------------------------------------------
    #
    async def process_reimbursement_request(self, payload: PaymentPayload):
        """ Process reimbursement request.

         Implemented logic:
           - Get customer billing data and amount-to-reimburse from the CustomerService.
           - Send the reimbursement request to the external Credit Card Company.
           - Update payment status in DB collection api_db.payments.

        :param payload: Reimbursement request data.
        :raise HTTPException [500]: when processing request failed.
        :raise HTTPException [400]: when HTTP POST response != 201 or 202.
        :raise HTTPException [500]: when connection with CustomerService failed.
        """
        url = None

        try:
            meta = payload.metadata
            root = await self.cache.get('CustomerService')
            items = [item.dict() for item in payload.items]

            # Get Customer Credit Card information.
            async with AsyncClient() as client:
                url = f"{root}/v1/customers/{meta.customer_id}/billing"
                resp = await client.post(url=url, json=items,
                                         timeout=config.url_timeout)

            if resp.status_code != 201:
                errmsg = f"Failed CustomerService POST request for URL " \
                         f"{url} - [{resp.status_code}: {resp.json()['detail']}]."
                raise RuntimeError(errmsg)

            # Reimburse the Customer credit card.
            url = "http://fictitious.com/v1/payments/callback"
            billing = BillingPayload(caller_id=meta.order_id,
                                     callback_url=url, **resp.json())
            await self._reimburse_credit_card(billing)

        except RuntimeError as why:
            logger.error(f'{why}')
            raise HTTPException(status_code=400, detail=f'{why}')

        except ConnectTimeout:
            errmsg = f'No connection with CustomerService on URL {url}'
            logger.critical(errmsg)
            raise HTTPException(status_code=500, detail=errmsg)

        except BaseException as why:
            logger.critical(f'Failed processing payment request => {why}')
            raise HTTPException(status_code=500, detail=f'{why}')

    # ---------------------------------------------------------
    #
    async def process_response(self, payload: BillingCallback) -> BillingCallback:
        """ Process payment/reimbursement callback response.

         Implemented logic:
           - Extract payment Order from DB using payload caller_id.
           - Store updated billing data in DB collection api_db.payments.
           - Send the billing response to the metadata requester using RabbitMQ.

        :param payload: Payment callback response data.
        :return: Received payload.
        :raise HTTPException [404]: when caller_id does not exist in DB.
        """
        try:
            payment = await self.repo.read(payload.caller_id)

            if not payment:
                errmsg = f"Caller ID '{payload.caller_id}' does " \
                         f"not exist in DB api_db.payments."
                raise RuntimeError(errmsg)

            # Prepare payment response.
            response = PaymentResponse(status=payload.status, metadata=payment.metadata)

            # Update payment in DB.
            payment.status = payload.status
            await self.repo.update(payment)

            # Send response message to requester.
            await self.client.send_message(message=response.dict(),
                                           queue=payment.metadata.receiver)

            logger.info(f"Sent Payment response to {payment.metadata.receiver} "
                        f"with status '{payload.status}' for Order '{payload.caller_id}'.")

            return payment

        except RuntimeError as why:
            logger.error(f'{why}')
            raise HTTPException(status_code=404, detail=f'{why}')
