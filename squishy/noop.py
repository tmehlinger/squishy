from __future__ import absolute_import

import logging
import pprint

from boto3 import Session


def noop_callback(message):
    logging.debug(pprint.pformat(message))


def noop_session_factory():
    return Session()
