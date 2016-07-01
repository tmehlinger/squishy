from __future__ import absolute_import

from multiprocessing import pool
import signal

from .._compat import viewkeys
from ..logging import get_logger
from .base import BaseWorker


class MultiprocessingWorker(BaseWorker):
    def process_messages(self, messages):
        result_to_message = {}
        processed = []

        self.logger.debug('processing %d messages', len(messages))
        for message in messages:
            # ThreadPoolExecutor will throw a RuntimeException if we try
            # to # submit while it's shutting down. If we encounter a
            # RuntimeError, # immediately stop trying to submit new tasks;
            # they will get requeued after the interval configured on the
            # queue's policy.
            try:
                result = self.pool.apply_async(self.func, (message,))
            except:
                self.logger.exception('cannot submit jobs to pool')
                raise
            else:
                result_to_message[result] = message

        while result_to_message:
            keys = list(viewkeys(result_to_message))
            for result in keys:
                message = result_to_message[result]
                try:
                    result.get()
                except:
                    self.logger.exception('exception processing message %s',
                                          message['MessageId'])
                else:
                    del result_to_message[result]
                    processed.append(message)

        return processed

    def shutdown(self):
        self.pool.close()
        self.pool.join()


def init_process_pool():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)


class ProcessPoolWorker(MultiprocessingWorker):
    def __init__(self, func, pool_size=4, timeout=None):
        # The signal handler for the consumer exists only in the parent
        # process. If we don't give children their own noop signal handler,
        # any signal propagated to them by the parent will cause them to throw
        # an exception and terminate.
        super(ProcessPoolWorker, self).__init__(func, pool_size=pool_size,
                                                timeout=timeout)
        self.pool =  pool.Pool(processes=pool_size,
                               initializer=init_process_pool)
        self.logger = get_logger(__name__)


class ThreadPoolWorker(MultiprocessingWorker):
    def __init__(self, func, pool_size=4, timeout=None):
        super(ThreadPoolWorker, self).__init__(func, pool_size=pool_size,
                                               timeout=timeout)
        self.pool = pool.ThreadPool(processes=pool_size)
        self.logger = get_logger(__name__)
