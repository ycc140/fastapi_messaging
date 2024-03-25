# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-24 19:33:51
     $Rev: 72
"""

# Third party modules
from pydantic import BaseModel, Field

# Local modules
from ..repository.models import Status, MetadataSchema


# ---------------------------------------------------------
#
class PaymentResponse(BaseModel):
    """ Representation of a Payment Response in the system.

    :ivar metadata: Order metadata in the system.
    :ivar status: Payment state.
    """
    metadata: MetadataSchema
    status: Status = Field(send_example=Status.PAID)
