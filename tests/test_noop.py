from __future__ import absolute_import

from boto3 import Session

from squishy import noop


def test_noop_callback():
    assert noop.noop_callback(None) is None


def test_noop_session_factory():
    assert isinstance(noop.noop_session_factory(), Session)
