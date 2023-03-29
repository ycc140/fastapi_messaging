# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-29 19:37:08
     $Rev: 45
"""

# BUILTIN modules
from pathlib import Path
from contextlib import asynccontextmanager

# Third party modules
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Local modules
from .api import api
from ..config.setup import config
from ..repository.db import Engine
from .health_manager import HealthManager
from ..repository.url_cache import UrlCache
from .api.schemas import HealthSchema, HealthStatusError
from ..tools.custom_logging import create_unified_logger
from .api.documentation import (servers, license_info,
                                tags_metadata, description)
from ..repository.payment_data_adapter import PaymentsRepository


# ---------------------------------------------------------
#
class Service(FastAPI):

    def __init__(self, *args, **kwargs):
        """ This class adds RabbitMQ message consumption and unified logging.

        :param args: named arguments.
        :param kwargs: key-value pair arguments.
        """
        super().__init__(*args, **kwargs)

        self.level, self.logger = create_unified_logger(config.service_log_level)


# ---------------------------------------------------------
#
@asynccontextmanager
async def lifespan(service: Service):
    await startup(service)
    yield
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
app.include_router(api.router)

# Needed for OpenAPI Markdown images to be displayed.
static_path = Path(__file__).parent.parent.parent.parent / 'design_docs'
app.mount("/static", StaticFiles(directory=static_path))


# ---------------------------------------------------------
#
@app.get(
    '/health',
    response_model=HealthSchema,
    tags=["health check endpoint"],
    responses={500: {"model": HealthStatusError}},
)
async def health_check() -> HealthSchema:
    """ **Health check endpoint.** """

    content = await HealthManager(UrlCache(config.redis_url),
                                  PaymentsRepository()).get_status()
    response_code = (200 if content.status else 500)

    return JSONResponse(status_code=response_code, content=content.dict())


# ---------------------------------------------------------
#
async def startup(service: Service):
    """ Initialize MongoDB connection. """

    service.logger.info('Establishing MongoDB connection...')
    await Engine.connect_to_mongo()


# ---------------------------------------------------------
#
async def shutdown(service: Service):
    """ Close MongoDB connection. """

    service.logger.info('Disconnecting from MongoDB...')
    await Engine.close_mongo_connection()
