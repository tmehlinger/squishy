from __future__ import absolute_import

import logging
import pprint

from boto3 import Session


log = logging.getLogger(__name__)


noop_dummy = object()


def noop_callback(message):
    log.info(pprint.pformat(message))


class NoopCallback(object):  # pylint: disable=too-few-public-methods
    def __call__(self, message):
        log.info(pprint.pformat(message))

noop_callback_obj = NoopCallback()


def noop_session_factory():
    return Session()
