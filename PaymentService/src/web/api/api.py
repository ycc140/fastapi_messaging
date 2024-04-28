# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-28 15:22:00
     $Rev: 9
"""

# Third party modules
from fastapi import APIRouter, Depends, status

# Local modules
from ...broker.unit_of_work import UnitOfWork
from ...repository.interface import IRepository
from ...repository import get_payment_repository
from .payment_api_adapter import PaymentApiAdapter
from ...core.security import validate_authentication
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
async def create_payment(
        payload: PaymentPayload,
        repo: IRepository = Depends(get_payment_repository)
) -> PaymentAcknowledge:
    """ **Process payment request.**

    :param payload: Payment request body data.
    :param repo: PaymentRepository object with an active DB session.
    :return: Payment acknowledge model.
    """
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
async def reimburse_payment(
        payload: PaymentPayload,
        repo: IRepository = Depends(get_payment_repository)
) -> PaymentAcknowledge:
    """ **Process reimbursement request.**

    :param payload: Payment request body data.
    :param repo: PaymentRepository object with an active DB session.
    :return: Payment acknowledge model.
    """
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
async def billing_response(
        payload: BillingCallback,
        repo: IRepository = Depends(get_payment_repository)

) -> BillingCallback:
    """ **Process callback response.**

    :param payload: Billing callback request body data.
    :param repo: PaymentRepository object with an active DB session.
    :return: Billing callback model.
    """
    async with UnitOfWork() as worker:
        service = PaymentApiAdapter(repo, worker)
        return await service.process_response(payload)
