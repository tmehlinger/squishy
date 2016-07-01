from __future__ import absolute_import

import logging
import sys


if sys.version_info[:2] == (2, 6):
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
else:
    from logging import NullHandler


def get_logger(name, handler=None):
    logger = logging.getLogger(name)
    logger.addHandler(handler or NullHandler())
    return logger
