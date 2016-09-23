import time

import pytest

from squishy.consumer import SqsConsumer


def test_parse_region_name(queue):
    rn = SqsConsumer.parse_region_name(queue.url)
    assert rn == 'us-east-1'


def test_parse_invalid_region_name(queue):
    url = 'https://invalid.bike/does/not/work'
    with pytest.raises(RuntimeError):
        SqsConsumer.parse_region_name(url)


def test_long_poll_messages(consumer, queue, worker):
    queue.send_message(MessageBody='testing')
    consumer._poll_messages()
    assert len(worker.process_messages_called_with) == 1


def test_short_poll_messages(consumer, queue, worker):
    queue.send_message(MessageBody='testing')
    consumer.use_short_polling = True
    consumer._poll_messages()
    assert len(worker.process_messages_called_with) == 1


def test_delete_messages(consumer, queue):
    queue.send_message(MessageBody='testing')
    messages = queue.receive_messages()
    assert len(messages) == 1
    failed = consumer._delete_messages(messages)
    assert len(failed) == 0


def test_run(consumer, queue, worker):
    # kind of a hack... need to give the consumer enough time to to have
    # consumed a message and dispatched it to the worker
    queue.send_message(MessageBody='testing')
    consumer.run(join_timeout=2)
    time.sleep(1)
    assert len(worker.process_messages_called_with) == 1
    assert consumer.should_stop.is_set()


def test_stop(consumer, worker):
    consumer.run()
    consumer.stop(None, None)
    assert consumer.should_stop.is_set()
    assert worker.shutdown_called
