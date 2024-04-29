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

# Third party modules
from fastapi import APIRouter, Depends, status

# Local modules
from .payment_api_adapter import PaymentApiAdapter
from ...broker.unit_of_work import UnitOfBrokerWork
from ...core.security import validate_authentication
from ...repository.unit_of_work import UnitOfRepositoryWork
from .models import (PaymentAcknowledge, BillingCallback,
                     ApiError, ConnectError, PaymentPayload)

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
async def create_payment(payload: PaymentPayload) -> PaymentAcknowledge:
    """ **Process payment request.**

    :param payload: Payment request body data.
    :return: Payment acknowledge model.
    """
    async with UnitOfRepositoryWork() as repo:
        service = PaymentApiAdapter(repo)
        await service.process_payment_request(payload)
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
async def reimburse_payment(payload: PaymentPayload) -> PaymentAcknowledge:
    """ **Process reimbursement request.**

    :param payload: Payment request body data.
    :return: Payment acknowledge model.
    """
    async with UnitOfRepositoryWork() as repo:
        service = PaymentApiAdapter(repo)
        await service.process_reimbursement_request(payload)
        return PaymentAcknowledge(order_id=payload.metadata.order_id)


# ---------------------------------------------------------
#
@ROUTER.post(
    '/callback',
    response_model=BillingCallback,
    status_code=status.HTTP_201_CREATED,
)
async def billing_response(payload: BillingCallback) -> BillingCallback:
    """ **Process callback response.**

    :param payload: Billing callback request body data.
    :return: Billing callback model.
    """
    async with UnitOfRepositoryWork() as repo:
        async with UnitOfBrokerWork() as worker:
            service = PaymentApiAdapter(repo, worker)
            return await service.process_response(payload)
