# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-19 11:40:10
     $Rev: 7
"""

# Local modules
from .mongo_repository import MongoRepository
from .payment_data_adapter import PaymentRepository


payments_repository = PaymentRepository(MongoRepository())
""" Repository injected with MongoDB implementation. """
