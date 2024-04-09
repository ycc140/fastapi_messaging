# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-04-09 05:37:36
     $Rev: 3
"""

# Local modules
from ...core.setup import config

health_example = {
    "status": True,
    "cert_remaining_days": 820,
    "version": f"{config.version}",
    "name": f"{config.service_name}",
    "resources": [
        {
            "name": "Certificate.valid",
            "status": True
        },
        {
            "name": "MongoDb",
            "status": True
        },
        {
            "name": "CustomerService",
            "status": True
        },
    ]
}
""" OpenAPI health response documentation. """

billing_example = {
    "IssuingNetwork": "MASTERCARD",
    "CardNumber": "5485848512008744",
    "Bank": "NORDEA BANK AB",
    "Name": "Barirah Chou",
    "Address": "Stallstigen 30",
    "Country": "SWEDEN",
    "MoneyRange": "$804",
    "CVV": "808",
    "Expiry": "07/2030",
}
""" OpenAPI CreditCardSchema example documentation. """

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

callback_documentation = {
    "status": {'example': 'paymentPaid',
               'description': 'Credit Card billing/reimburse result.'},
    "caller_id": {'example': 'b76d019f-5937-4a14-8091-1d9f18666c93',
                  'description': 'Internal Order ID of the billed Order.'},
    "transaction_id": {'example': 'f2861560-e9ed-4463-955f-0c55c3b416fb',
                       'description': 'Credit Card company transaction ID.'},
}
""" OpenAPI BillingCallback parameters documentation. """

tags_metadata = [
    {
        "name": "Payments",
        "description": f"The ***{config.service_name}*** handle payments for the "
                       f"following Credit Cards: `VISA`, `Mastercard`, `Eurocard`.",
    }
]
""" OpenAPI Payments endpoint documentation. """

license_info = {
    "name": "License: Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
}
""" OpenAPI license documentation. """

servers = [
    {
        "url": "https://127.0.0.1:8001",
        "description": "URL for local development and testing"
    },
    {
        "url": "https://coffeemesh-staging.com",
        "description": "staging server for testing purposes only"
    },
    {
        "url": "https://coffeemesh.com",
        "description": "main production server"
    },
]
""" OpenAPI API platform servers. """

description = """
<img width="65%" align="right" src="/static/order_container_diagram.png"/>
**An example on how to use FastAPI and RabbitMQ to create a RESTful API for responses that takes some time to 
process.** 

This service handles Customer Credit Card payments using external Credit Card Companies. Required payload is 
 `PaymentPayload` and the response is `PaymentResponse`. Both schemas are described in detail under Schemas below.

<br>**The following HTTP status codes are returned:**
  * `200:` Successful Health response.
  * `201:` Successful POST callback response.
  * `202:` Successful POST response.
  * `400:` Failed internal Microservice API call.
  * `422:` Validation error, supplied payload is incorrect.
  * `500:` Failed to connect to internal MicroService.
  * `500:` Failed Health response.
<br><br>
---
"""
""" OpenAPI main Payments documentation. """
