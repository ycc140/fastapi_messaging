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

payment_documentation = {
    "receiver": {'example': 'OrderService',
                 'description': 'Requesting service.'},
    "status": {'description': 'Payment workflow status.'},
    "created": {'example': "`2023-03-10T12:15:23.123234`",
                'description': 'Timestamp when the Payment was created.'},
    "id": {'example': "`dbb86c27-2eed-410d-881e-ad47487dd228`",
           'description': 'Order ID: A unique identifier for an existing Order.'},
    "transaction_id": {'example': 'f2861560-e9ed-4463-955f-0c55c3b416fb',
                       'description': 'Transaction ID for the Credit Card company for the current Order.'},
}
