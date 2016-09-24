from __future__ import absolute_import

import logging


def get_logger(name, handler=None):
    logger = logging.getLogger(name)
    logger.addHandler(handler or logging.NullHandler())
    return logger
