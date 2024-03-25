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
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

# local modules
from ..health_manager import HealthManager
from .models import HealthResponseModel, HealthStatusError

# Constants
ROUTER = APIRouter(prefix="/health", tags=["Health endpoint"])
""" Health API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.get(
    '',
    response_model=HealthResponseModel,
    responses={500: {"model": HealthStatusError}},
)
async def health_check(request: Request) -> JSONResponse:
    """ **Health check endpoint.**

    :param request: FastAPI request object.
    :return: Service health response.
    """

    content = await HealthManager(request.app.rabbit_client).get_status()
    response_code = (200 if content.status else 500)

    return JSONResponse(status_code=response_code,
                        content=content.model_dump())
