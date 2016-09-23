from __future__ import absolute_import

import logging
import pprint

from boto3 import Session


log = logging.getLogger(__name__)


def noop_callback(message):
    log.info(pprint.pformat(message))


def noop_session_factory():
    return Session()
