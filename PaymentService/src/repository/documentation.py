# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-27 21:26:58
     $Rev: 8
"""

metadata_example = {
    "receiver": "OrderService",
    "order_id": 'b76d019f-5937-4a14-8091-1d9f18666c93',
    "customer_id": 'f2861560-e9ed-4463-955f-0c55c3b416fb',
}
""" OpenAPI MetadataSchema example documentation. """

metadata_documentation = {
    "receiver": {'example': 'OrderService',
                 'description': 'Requesting service.'},
    "order_id": {'example': 'b76d019f-5937-4a14-8091-1d9f18666c93',
                 'description': 'Order ID of the Order currently being handled.'},
    "customer_id": {'example': 'f2861560-e9ed-4463-955f-0c55c3b416fb',
                    'description': 'Customer ID for the Order currently being handled.'},
}
""" OpenAPI MetadataSchema parameters documentation. """

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
""" OpenAPI payment documentation. """
