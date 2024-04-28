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

# BUILTIN modules
from typing import Protocol


# -----------------------------------------------------------------------------
#
class IBroker(Protocol):
    """ Payment Broker Interface class. """

    # ---------------------------------------------------------
    #
    async def publish(self, queue: str, message: dict):
        """ Publish a message on specified RabbitMQ queue asynchronously.

        :param queue: Publishing queue.
        :param message: Message to be published.
        """

    # ---------------------------------------------------------
    #
    def is_connected(self) -> bool:
        """ Return connection status. """
