from datetime import datetime
import signal
from threading import Event, Thread

from boto3 import Session

from .logging import get_logger


class SqsConsumer(object):
    """Create a new consumer with the given queue URL. The consumer calls
    `callback` to each message.

    :param queue_url: URL of the queue to consume.
    :type queue_url: str
    :param callback: Function to call to handle incoming messages.
    :type callback: function
    :param session: Optional `boto3.Session` for providing customized
        authentication. See the documentation on authentication for more
        information.
    :type session: boto3.Session
    :param worker: The worker instance.
    :type worker: squishy.workers.BaseWorker
    :param use_short_polling: Force the consumer to do short polling on
        the queue.
    :type use_short_polling: bool
    :param polling_timeout: Time interval in seconds to poll the queue.
    :type polling_timeout: int
    :param polling_count: The number of messages to fetch in a single call
        to `get_message`.
    :type polling_count: int
    """

    def __init__(self, queue_url, worker, session=None,
                 use_short_polling=False, polling_timeout=10,
                 polling_count=10):
        self.use_short_polling = use_short_polling
        self.polling_timeout = polling_timeout
        self.polling_count = polling_count

        self.session = session or Session()
        self.sqs = self.session.client('sqs')
        self.queue_url = queue_url

        self.logger = get_logger(__name__)

        self.should_stop = Event()
        self.poller_thread = Thread(group=None, target=self._poll_messages)
        self.worker = worker

    def _poll_messages(self):
        while not self.should_stop.is_set():
            start = datetime.utcnow()
            self.logger.debug('polling for messages')

            kw = {
                'QueueUrl': self.queue_url,
                'MaxNumberOfMessages': self.polling_count,
            }
            # Note: If we're long polling, the call to ReceiveMessage block
            # for `polling_timeout` seconds.
            if not self.use_short_polling:
                kw['WaitTimeSeconds'] = self.polling_timeout
            envelope = self.sqs.receive_message(**kw)

            messages = envelope.get('Messages', [])
            finished = self.worker.process_messages(messages)

            self._delete_messages(finished)

            # If we're long polling, we jump to the top of the loop here. If
            # not... see below.
            if not self.use_short_polling:
                continue

            # We try to iterate on regular intervals by finding the amount of
            # elapsed time to process the last batch of messages, then
            # subtract that from the configured timeout. If we ran over the
            # timeout, force the timeout to 0 so we immediately jump to the
            # top of the loop. This gives us more regular, predictable
            # behavior and also prevents us from beating the crap out of the
            # SQS API for no good reason.
            delta = datetime.utcnow() - start
            elapsed = delta.days * 86400 + delta.seconds
            timeout = self.polling_timeout - elapsed
            if self.should_stop.wait(timeout=max(0, timeout)):
                break

    def _delete_messages(self, messages):
        if not messages:
            return

        entries = [{'Id': message['MessageId'],
                    'ReceiptHandle': message['ReceiptHandle']}
                   for message in messages]
        self.sqs.delete_message_batch(QueueUrl=self.queue_url,
                                      Entries=entries)

    def run(self):
        """Run the consumer."""
        self.logger.warning('starting up')

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        self.poller_thread.start()
        while self.poller_thread.isAlive():
            self.poller_thread.join(1)

        self.logger.info('done')

    def stop(self, signum, _):
        self.logger.warning('got signal %s, stopping', signum)
        self.should_stop.set()
        self.worker.shutdown()
