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

# BUILTIN modules
import os
import signal
import asyncio

# BUILTIN modules
from pathlib import Path
from contextlib import asynccontextmanager

# Third party modules
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Local modules
from ..core.setup import config
from .api import api, health_route
from ..repository.db import Engine
from ..tools.rabbit_client import RabbitClient
from ..tools.custom_logging import create_unified_logger
from .api.documentation import (servers, license_info,
                                tags_metadata, description)


# ---------------------------------------------------------
#
class Service(FastAPI):
    """ This class extends the FastAPI class for the PaymentService API.

    The following functionality is added:
      - unified logging.
      - includes API router.
      - Instantiates a RabbitMQ client.
      - Defines a static path for images in the documentation.

    :ivar rabbit_client: RabbitMQ client.
    :type rabbit_client: `RabbitClient`
    :ivar logger: Unified loguru logger object.
    :type logger: loguru.logger
    """

    def __init__(self, *args: int, **kwargs: dict):
        """ This class adds RabbitMQ message consumption and unified logging.

        :param args: Named arguments.
        :param kwargs: Key-value pair arguments.
        """
        super().__init__(*args, **kwargs)

        # Needed for OpenAPI Markdown images to be displayed.
        static_path = Path(__file__).parent.parent.parent.parent / 'design_docs'
        self.mount("/static", StaticFiles(directory=static_path))

        self.rabbit_client = RabbitClient(config.rabbit_url)

        self.include_router(api.ROUTER)
        self.include_router(health_route.ROUTER)

        self.logger = create_unified_logger()


# ---------------------------------------------------------
#
@asynccontextmanager
async def lifespan(service: Service):
    """ Define startup and shutdown application logic.

    :param service: FastAPI service.
    """
    try:
        await startup(service)
        yield

    except BaseException as why:
        service.logger.critical(f'MongoDB/RabbitMQ server is unreachable: {why.args[1]}.')

        # Needed for the log to be visible.
        await asyncio.sleep(0.1)

        # Stop the program since it's no point to continue.
        os.kill(os.getpid(), signal.SIGTERM)

    finally:
        await shutdown(service)


# ---------------------------------------------------------

app = Service(
    servers=servers,
    lifespan=lifespan,
    title=config.name,
    version=config.version,
    description=description,
    license_info=license_info,
    openapi_tags=tags_metadata,
)
""" The FastAPI application instance. """


# ---------------------------------------------------------
#
async def startup(service: Service):
    """ Initialize MongoDB connection.

    :param service: FastAPI service instance.
    """

    service.logger.info('Establishing MongoDB connection...')
    await Engine.create_db_connection()

    service.logger.info('Establishing RabbitMQ connection..')
    await service.rabbit_client.start()


# ---------------------------------------------------------
#
async def shutdown(service: Service):
    """ Close MongoDB connection.

    :param service: FastAPI service instance.
    """

    if service.rabbit_client.is_connected:
        service.logger.info('Disconnecting from RabbitMQ...')
        await service.rabbit_client.stop()

    service.logger.info('Disconnecting from MongoDB...')
    await Engine.close_db_connection()
