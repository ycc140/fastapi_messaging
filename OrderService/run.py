#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-20 22:57:08
     $Rev: 24
"""

# Third party modules
import uvicorn

# Local modules
from src.web.main import app


if __name__ == "__main__":

    uv_config = {'app': 'src.web.main:app', 'port': 8000,
                 'log_level': app.level, 'reload': True,
                 'log_config': {"disable_existing_loggers": False, "version": 1}}
    uvicorn.run(**uv_config)
