from __future__ import absolute_import


class BaseWorker(object):
    pool = None
    logger = None

    def __init__(self, func, pool_size=4, timeout=None):
        self.func = func
        self.pool_size = pool_size
        self.timeout = timeout

    def process_messages(self, messages):
        raise NotImplementedError('must be implemented by derived classes')

    def shutdown(self):
        raise NotImplementedError('must be implemented by derived classes')
