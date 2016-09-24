from __future__ import absolute_import


class NoopWorker(object):
    __name__ = 'NoopWorker'

    def __init__(self, *args, **kwargs):
        pass

    def process_messages(self, _):
        pass

    def shutdown(self):
        pass
