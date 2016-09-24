from __future__ import absolute_import

try:
    from concurrent import futures
except ImportError:
    raise RuntimeError('could not import concurrent.futures; did you forget'
                       'to install `futures` on Python 2.7?')

from ..logging import get_logger
from .base import BaseWorker


class FuturesWorker(BaseWorker):
    def process_messages(self, messages):
        future_to_message = {}
        processed = []

        self.logger.debug('processing %d messages', len(messages))
        for message in messages:
            # ThreadPoolExecutor/ProcessPoolExecutor will throw a
            # RuntimeException if we try to submit while it's shutting down.
            # If we encounter a RuntimeError, immediately stop trying to
            # submit new tasks; they will get requeued after the interval
            # configured on the queue's policy.
            try:
                future = self.pool.submit(self.func, message)
            except RuntimeError:
                self.logger.exception('cannot submit jobs to pool')
                raise
            else:
                future_to_message[future] = message

        for future in futures.as_completed(future_to_message,
                                           timeout=self.timeout):
            message = future_to_message.pop(future)
            try:
                future.result()
            except:
                self.logger.exception('exception processing message %s',
                                      message.message_id)
            else:
                processed.append(message)

        return processed

    def shutdown(self):
        self.pool.shutdown()


class ProcessPoolWorker(FuturesWorker):
    def __init__(self, func, pool_size=4, timeout=None):
        super(ProcessPoolWorker, self).__init__(func, pool_size=pool_size,
                                                timeout=timeout)
        self.pool = futures.ProcessPoolExecutor(max_workers=pool_size)
        self.logger = get_logger(__name__)


class ThreadPoolWorker(FuturesWorker):
    def __init__(self, func, pool_size=4, timeout=None):
        super(ThreadPoolWorker, self).__init__(func, pool_size=pool_size,
                                               timeout=timeout)
        self.pool = futures.ThreadPoolExecutor(max_workers=pool_size)
        self.logger = get_logger(__name__)
