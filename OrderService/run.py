#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-25 00:13:58
     $Rev: 73
"""

# BUILTIN modules
from contextlib import suppress

# Third party modules
import uvicorn

# Local modules
from src.config.setup import config

# As soon as the SSL certificates are added, the shutdown period is
# 30 seconds, unless the "timeout_graceful_shutdown" below is used.
uv_config = {'log_level': config.service_log_level,
             'ssl_keyfile': "certs/private-key.pem",
             'ssl_certfile': "certs/public-cert.pem",
             'app': 'src.web.main:app', 'port': 8000,
             'timeout_graceful_shutdown': 1, 'reload': True,
             'log_config': {"disable_existing_loggers": False, "version": 1}}
""" uvicorn startup parameters. """

with suppress(RuntimeError, KeyboardInterrupt):
    uvicorn.run(**uv_config)
