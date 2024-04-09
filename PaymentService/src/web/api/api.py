# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-09 06:22:27
     $Rev: 6
"""

# Third party modules
from fastapi import APIRouter, Request, Depends, status

# Local modules
from ...core.setup import config
from ...repository.url_cache import UrlServiceCache
from ...business.payment_handler import PaymentLogic
from ...core.security import validate_authentication
from .models import (PaymentAcknowledge, BillingCallback,
                     ApiError, ConnectError, PaymentPayload)
from ...repository.payment_data_adapter import payments_repository

# Constants
ROUTER = APIRouter(prefix="/v1/payments", tags=["Payments"],
                   dependencies=[Depends(validate_authentication)])
""" Payments API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post(
    '',
    response_model=PaymentAcknowledge,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ApiError},
        500: {'model': ConnectError}}
)
async def create_payment(payload: PaymentPayload,
                         request: Request) -> PaymentAcknowledge:
    """ **Process payment request.**

    :param payload: Payment request body data.
    :param request: Request class.
    :return: Payment acknowledge model.
    """
    worker = PaymentLogic(repository=payments_repository,
                          client=request.app.rabbit_client,
                          cache=UrlServiceCache(config.redis_url))
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
        500: {'model': ConnectError}}
)
async def reimburse_payment(payload: PaymentPayload,
                            request: Request) -> PaymentAcknowledge:
    """ **Process reimbursement request.**

    :param payload: Payment request body data.
    :param request: Request class.
    :return: Payment acknowledge model.
    """
    worker = PaymentLogic(repository=payments_repository,
                          client=request.app.rabbit_client,
                          cache=UrlServiceCache(config.redis_url))
    await worker.process_reimbursement_request(payload)
    return PaymentAcknowledge(order_id=payload.metadata.order_id)


# ---------------------------------------------------------
#
@ROUTER.post(
    '/callback',
    response_model=BillingCallback,
    status_code=status.HTTP_201_CREATED,
)
async def billing_response(payload: BillingCallback,
                           request: Request) -> BillingCallback:
    """ **Process callback response.**

    :param payload: Billing callback request body data.
    :param request: Request class.
    :return: Billing callback model.
    """
    worker = PaymentLogic(repository=payments_repository,
                          client=request.app.rabbit_client,
                          cache=UrlServiceCache(config.redis_url))
    return await worker.process_response(payload)
