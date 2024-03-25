#!/usr/bin/env python
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

# BUILTIN modules
import asyncio
import argparse

# Local modules
from src.config.setup import config
from src.tools.rabbit_client import RabbitClient

# Constants
PAYLOAD = {
    "DeliveryService": {
        "delivery_id": "76d019f-5937-4a14-8091-1d9f18666c93",
        "metadata":
            {
                "receiver": "OrderService",
                "customer_id": "f2861560-e9ed-4463-955f-0c55c3b416fb"
            }
    },
    "KitchenService": {
        "kitchen_id": "b4d7bb48-7b56-45c8-9eb3-dc6e96c09172",
        "metadata":
            {
                "receiver": "OrderService",
                "customer_id": "f2861560-e9ed-4463-955f-0c55c3b416fb"
            }
    }
}
""" Service response payload messages. """


# ---------------------------------------------------------
#
def _build_message(pid: int, order_id: str) -> dict:
    """ Build response message

    :param pid: Payload ID
    :param order_id: Order ID
    :return: response message.
    """
    message = None

    match pid:
        case 1:
            message = PAYLOAD['DeliveryService']
            message['status'] = 'driverAvailable'
        case 2:
            message = PAYLOAD['KitchenService']
            message['status'] = 'cookingMeal'
        case 3:
            message = PAYLOAD['KitchenService']
            message['status'] = 'cookingDone'
        case 4:
            message = PAYLOAD['KitchenService']
            message['status'] = 'pickedUp'
        case 5:
            message = PAYLOAD['DeliveryService']
            message['status'] = 'inTransit'
        case 6:
            message = PAYLOAD['DeliveryService']
            message['status'] = 'delivered'

    message['metadata']['order_id'] = order_id
    return message


# ---------------------------------------------------------
#
async def sender(args: argparse.Namespace):
    """ Send RabbitMQ payload test message.

    :param args: Command line arguments.
    """
    client = RabbitClient(config.rabbit_url)
    await client.start()
    message = _build_message(args.pid, args.order_id)
    await client.publish_message(message['metadata']['receiver'], message)
    print(f"message sent to '{message['metadata']['receiver']}'\n{message}")
    await client.stop()


# ---------------------------------------------------------

if __name__ == "__main__":
    Form = argparse.ArgumentDefaultsHelpFormatter
    description = 'A utility script that let you start the app choosing topic or queue handling.'
    parser = argparse.ArgumentParser(description=description, formatter_class=Form)
    parser.add_argument("order_id", type=str, help="Specify Order ID")
    parser.add_argument("pid", type=int, choices=list(range(1, 7)),
                        help="Specify payload ID")
    arguments = parser.parse_args()
    asyncio.run(sender(arguments))
