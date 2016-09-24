import logging

import squishy.logging as squishy_logging


def test_get_logger():
    name = 'testing'
    logger = squishy_logging.get_logger(name)
    assert logger.name == name
    assert isinstance(logger.handlers[0], logging.NullHandler)
