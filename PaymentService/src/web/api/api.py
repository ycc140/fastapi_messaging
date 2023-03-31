# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-31 20:31:23
     $Rev: 53
"""

# Third party modules
from fastapi import APIRouter, status

# Local modules
from ...config.setup import config
from ...repository.url_cache import UrlCache
from ...tools.rabbit_client import RabbitClient
from ...business.payment_handler import PaymentLogic
from .schemas import (PaymentAcknowledge, BillingCallback,
                      ApiError, ConnectError, PaymentPayload)
from ...repository.payment_data_adapter import PaymentsRepository

# Constants
router = APIRouter(prefix=f"/v1/payments", tags=[f"Payments"])
""" Payments API endpoint router. """


# ---------------------------------------------------------
#
@router.post(
    '',
    response_model=PaymentAcknowledge,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ApiError},
        500: {'model': ConnectError}}
)
async def create_payment(payload: PaymentPayload) -> PaymentAcknowledge:
    """ **Process payment request.** """
    worker = PaymentLogic(repository=PaymentsRepository(),
                          cache=UrlCache(config.redis_url),
                          client=RabbitClient(config.rabbit_url))
    await worker.process_payment_request(payload)
    return PaymentAcknowledge(order_id=payload.metadata.order_id)


# ---------------------------------------------------------
#
@router.post(
    '/reimburse',
    response_model=PaymentAcknowledge,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ApiError},
        500: {'model': ConnectError}}
)
async def reimburse_payment(payload: PaymentPayload) -> PaymentAcknowledge:
    """ **Process reimbursement request.** """
    worker = PaymentLogic(repository=PaymentsRepository(),
                          cache=UrlCache(config.redis_url),
                          client=RabbitClient(config.rabbit_url))
    await worker.process_reimbursement_request(payload)
    return PaymentAcknowledge(order_id=payload.metadata.order_id)


# ---------------------------------------------------------
#
@router.post(
    '/callback',
    response_model=BillingCallback,
    status_code=status.HTTP_201_CREATED,
)
async def billing_response(payload: BillingCallback) -> BillingCallback:
    """ **Process callback response.** """
    worker = PaymentLogic(repository=PaymentsRepository(),
                          cache=UrlCache(config.redis_url),
                          client=RabbitClient(config.rabbit_url))
    return await worker.process_response(payload)
