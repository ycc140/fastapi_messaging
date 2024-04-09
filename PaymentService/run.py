#!/usr/bin/env python
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

# Third party modules
import uvicorn
import ujson as json

# Local modules
from src.web.main import app
from src.core.setup import config

if __name__ == "__main__":
    # As soon as the SSL certificates are added, the shutdown period is
    # 30 seconds, unless the "timeout_graceful_shutdown" below is used.
    uv_config = {'log_level': config.service_log_level,
                 'ssl_keyfile': "certs/private-key.pem",
                 'ssl_certfile': "certs/public-cert.pem",
                 'app': 'src.web.main:app', 'port': 8001,
                 'timeout_graceful_shutdown': 1, 'reload': True,
                 'log_config': {"disable_existing_loggers": False, "version": 1}}
    """ uvicorn startup parameters. """

    # So you can se test the handling of different log levels.
    app.logger.info(f'{config.name} v{config.version} is initializing...')

    # Log config values for testing purposes.
    app.logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')

    uvicorn.run(**uv_config)
