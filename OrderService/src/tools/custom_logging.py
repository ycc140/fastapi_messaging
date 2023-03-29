# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-25 17:47:36
     $Rev: 42
"""

# BUILTIN modules
import sys
import logging
from typing import cast
from types import FrameType

# Third party modules
from loguru import logger


# ---------------------------------------------------------
#
class InterceptHandler(logging.Handler):
    """ Logs to loguru from Python logging module. """

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name

        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2

        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info).log(
            level,
            record.getMessage()
        )


# ---------------------------------------------------------
#
def create_unified_logger(log_level: str) -> tuple:
    """ Return unified Loguru logger object.

    :return: unified Loguru logger object.
    """

    level = log_level

    # Remove all existing loggers.
    logger.remove()

    # Create a basic Loguru logging config.
    logger.add(
        diagnose=True,
        backtrace=True,
        sink=sys.stderr,
        level=level.upper(),
    )

    # Prepare to incorporate python standard logging.
    seen = set()
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    for logger_name in logging.root.manager.loggerDict.keys():

        if logger_name not in seen:
            seen.add(logger_name.split(".")[0])
            mod_logger = logging.getLogger(logger_name)
            mod_logger.handlers = [InterceptHandler(level=level.upper())]
            mod_logger.propagate = False

    return level, logger.bind(request_id=None, method=None)
