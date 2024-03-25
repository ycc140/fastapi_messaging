# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-22 20:51:42
     $Rev: 69
"""

# Third party modules
from fastapi import APIRouter, Request, Depends, status

# Local modules
from ...config.setup import config
from ...repository.url_cache import UrlServiceCache
from ...business.payment_handler import PaymentLogic
from ...tools.security import validate_authentication
from .models import (PaymentAcknowledge, BillingCallback,
                     ApiError, ConnectError, PaymentPayload)
from ...repository.payment_data_adapter import payments_repository

# Constants
ROUTER = APIRouter(prefix="/v1/payments", tags=["Payments"])
""" Payments API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post(
    '',
    response_model=PaymentAcknowledge,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ApiError},
        500: {'model': ConnectError}},
    dependencies=[Depends(validate_authentication)]
)
async def create_payment(payload: PaymentPayload,
                         request: Request) -> PaymentAcknowledge:
    """ **Process payment request.**

    :param payload: Payment request body data.
    :param request: Request class.
    :return: Payment acknowledge model.
    """
    worker = PaymentLogic(repository=payments_repository,
                          cache=UrlServiceCache(config.redis_url),
                          client=request.app.rabbit_client)
    await worker.process_payment_request(payload)
    return PaymentAcknowledge(order_id=payload.metadata.order_id)


# ---------------------------------------------------------
#
@ROUTER.post(
    '/reimburse',
    response_model=PaymentAcknowledge,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ApiError},
        500: {'model': ConnectError}},
    dependencies=[Depends(validate_authentication)]
)
async def reimburse_payment(payload: PaymentPayload,
                            request: Request) -> PaymentAcknowledge:
    """ **Process reimbursement request.**

    :param payload: Payment request body data.
    :param request: Request class.
    :return: Payment acknowledge model.
    """
    worker = PaymentLogic(repository=payments_repository,
                          cache=UrlServiceCache(config.redis_url),
                          client=request.app.rabbit_client)
    await worker.process_reimbursement_request(payload)
    return PaymentAcknowledge(order_id=payload.metadata.order_id)


# ---------------------------------------------------------
#
@ROUTER.post(
    '/callback',
    response_model=BillingCallback,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_authentication)]
)
async def billing_response(payload: BillingCallback,
                           request: Request) -> BillingCallback:
    """ **Process callback response.**

    :param payload: Billing callback request body data.
    :param request: Request class.
    :return: Billing callback model.
    """
    worker = PaymentLogic(repository=payments_repository,
                          cache=UrlServiceCache(config.redis_url),
                          client=request.app.rabbit_client)
    return await worker.process_response(payload)
