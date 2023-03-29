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

order_documentation = {
    "status": {'description': 'Order workflow status.'},
    "updated": {'example': [{"`2023-03-10T12:15:23.123234`", "paymentPaid"}],
                'default': [], 'description': 'Order status change history.'},
    "when": {'example': "`2023-03-10T12:15:23.123234`",
             'description': 'Timestamp for the Order status change.'},
    "created": {'example': "`2023-03-10T12:15:23.123234`",
                'description': 'Timestamp when the Order was created.'},
    "id": {'example': "`dbb86c27-2eed-410d-881e-ad47487dd228`",
           'description': '**Order ID**: A unique identifier for an existing Order.'},
    "kitchen_id": {'default': None, 'example': 'b76d019f-5937-4a14-8091-1d9f18666c93',
                   'description': 'Kitchen ID for the Order meal being produced.'},
    "delivery_id": {'default': None, 'example': 'f2861560-e9ed-4463-955f-0c55c3b416fb',
                    'description': 'Delivery ID for the Order during delivered.'},
    "customer_id": {'example': 'f2861560-e9ed-4463-955f-0c55c3b416fb',
                    'description': 'Customer ID for the person that created the Order.'},
}
