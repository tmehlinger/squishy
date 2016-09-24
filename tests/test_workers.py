import uuid

import pytest

from squishy.workers import futures, multiprocessing


# we declare Callback, Errback and Message mocks here rather than using
# fixtures because pytest will mangle the namespace, meaning, the pickler
# inside some of the worker pools won't be able to serialize them to dispatch
# for processing
def callback(_):
    pass


def errback(_):
    raise ValueError('test error')


class Message(object):
    def __init__(self):
        self.message_id = str(uuid.uuid1())


@pytest.mark.parametrize('worker_cls', [
    futures.ProcessPoolWorker,
    futures.ThreadPoolWorker,
    multiprocessing.ProcessPoolWorker,
    multiprocessing.ThreadPoolWorker,
])
def test_process_messages(worker_cls):
    msg = Message()
    w = worker_cls(callback)
    to_delete = w.process_messages([msg])
    w.shutdown()
    assert len(to_delete) == 1


@pytest.mark.parametrize('worker_cls', [
    futures.ProcessPoolWorker,
    futures.ThreadPoolWorker,
    multiprocessing.ProcessPoolWorker,
    multiprocessing.ThreadPoolWorker,
])
def test_process_messages_with_exception(worker_cls):
    msg = Message()
    w = worker_cls(errback)
    to_delete = w.process_messages([msg])
    w.shutdown()
    assert len(to_delete) == 0
