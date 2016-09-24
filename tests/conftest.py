import uuid

import boto3
import mock
import moto
import pytest

from squishy.consumer import SqsConsumer
from squishy.workers.base import BaseWorker


@pytest.fixture
def sqs(request):
    mock = moto.mock_sqs()
    mock.start()
    sqs = boto3.resource('sqs', region_name='us-east-1')
    request.addfinalizer(mock.stop)
    return sqs


@pytest.fixture
def queue(sqs):
    q = sqs.create_queue(QueueName='test-queue')
    q.set_attributes(Attributes={'VisibilityTimeout': '10'})
    return q


@pytest.fixture
def callback():
    def _callback(message):
        pass
    return mock.Mock(spec=_callback)


@pytest.fixture
def worker(callback):
    class MockWorker(BaseWorker):
        process_messages_called_with = None
        shutdown_called = False

        def __init__(self, func, **kwargs):
            super(MockWorker, self).__init__(func, **kwargs)

        def process_messages(self, messages):
            self.process_messages_called_with = messages

        def shutdown(self):
            self.shutdown_called = True

    return MockWorker(callback)


@pytest.fixture
def consumer(request, queue, worker):
    class MockEvent(object):
        is_set_was_called = False

        def is_set(self):
            if not self.is_set_was_called:
                self.is_set_was_called = True
                return False
            return True

        def set(self):
            pass

        def wait(self, *args, **kwargs):
            return True

    c = SqsConsumer(queue.url, worker, polling_timeout=0)
    c.should_stop = MockEvent()
    return c
