# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-24 19:33:51
     $Rev: 72
"""

# BUILTIN modules
import os
import site
from os import getenv
from pathlib import Path
from ssl import SSLContext
from typing import Type, Tuple

# Third party modules
from pydantic import Field
from pydantic_settings import (PydanticBaseSettingsSource,
                               BaseSettings, SettingsConfigDict)

# Constants
ENVIRONMENT = getenv('ENVIRONMENT', 'dev')
""" Current platform environment. """
MISSING_ENV = '>>> missing ENV value <<<'
""" Error message for missing values in the .env file. """
MISSING_SECRET = '>>> missing SECRETS file <<<'
""" Error message for missing secrets file. """
CERT_PATH = Path(__file__).parent.parent.parent / 'certs'
""" Local certificate path. """
SECRETS_DIR = ('/run/secrets'
               if os.path.exists('/.dockerenv')
               else f'{site.getuserbase()}/secrets')
""" This is where your secrets are stored (in Docker or locally). """
# noinspection PyNoneFunctionAssignment
SSL_CONTEXT = SSLContext().load_cert_chain(f'{CERT_PATH}/public-cert.pem',
                                           f'{CERT_PATH}/private-key.pem')
""" Define the SSL context certificate chain. """


# ---------------------------------------------------------
#
class Configuration(BaseSettings):
    """ Configuration parameters.

    :ivar model_config: Changes default settings in the BaseSettings class.
    :type model_config: SettingsConfigDict
    :ivar name: Microservice API name.
    :ivar version: Microservice API version.
    :ivar service_name: Microservice name.
    :ivar service_log_level:  Microservice log level.
    :ivar url_timeout: Timeout values used for http/https requests.
    :ivar service_api_key: Web sservice API key.
    :ivar mongo_url: The MongoDB URL.
    :ivar redis_url: The Redis URL.
    :ivar rabbit_url: The RabbitMQ URL.
    """
    model_config = SettingsConfigDict(secrets_dir=SECRETS_DIR,
                                      env_file_encoding='utf-8',
                                      env_file=Path(__file__).parent / '.env')

    # OpenAPI documentation.
    name: str = MISSING_ENV
    version: str = MISSING_ENV

    # Service parameters.
    service_name: str = MISSING_ENV
    service_log_level: str = MISSING_ENV

    # External resource parameters.
    url_timeout: tuple = (1.0, 5.0)
    service_api_key: str = MISSING_SECRET
    mongo_url: str = Field(MISSING_SECRET, alias=f'mongo_url_{ENVIRONMENT}')
    redis_url: str = Field(MISSING_SECRET, alias=f'redis_url_{ENVIRONMENT}')
    rabbit_url: str = Field(MISSING_SECRET, alias=f'rabbit_url_root_{ENVIRONMENT}')

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            env_settings: PydanticBaseSettingsSource,
            init_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """ Change source priority order (ignore environment values). """
        return init_settings, dotenv_settings, file_secret_settings


# ---------------------------------------------------------

config = Configuration()
""" Configuration parameters instance. """
