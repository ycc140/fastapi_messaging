# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-04-01 21:09:57
     $Rev: 56
"""

# BUILTIN modules
import site

# Third party modules
from dotenv import load_dotenv
from pydantic import BaseSettings

# Constants
MISSING_SECRET = '>>> missing SECRETS file <<<'
""" Error message for missing secrets file. """
MISSING_ENV = '>>> missing ENV value <<<'
""" Error message for missing values in the .env file. """


# ---------------------------------------------------------
#
class Configuration(BaseSettings):
    """ Configuration parameters. """

    # OpenAPI documentation.
    name: str = MISSING_ENV
    version: str = MISSING_ENV

    # Service parameters.
    service_name: str = MISSING_ENV
    service_log_level: str = MISSING_ENV

    # External resource parameters.
    url_timeout: tuple = (1.0, 5.0)
    mongo_url: str = MISSING_SECRET
    redis_url: str = MISSING_SECRET
    rabbit_url: str = MISSING_SECRET

    # Handles both local and Docker environments.
    class Config:
        secrets_dir = f'{site.USER_BASE}/secrets'


# ---------------------------------------------------------

# Note that the ".env" file is always implicitly loaded.
load_dotenv()

config = Configuration()
""" Configuration parameters instance. """
