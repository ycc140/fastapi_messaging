# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-21 22:20:47
     $Rev: 27
"""

# Third party modules
from pydantic import BaseModel, Field

# Local modules
from ..repository.models import Status
from ..web.api.schemas import MetadataSchema


# ---------------------------------------------------------
#
class PaymentResponse(BaseModel):
    """ Representation of a Payment Response in the system. """
    metadata: MetadataSchema
    status: Status = Field(send_example=Status.PAID)
