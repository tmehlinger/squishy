from __future__ import absolute_import

try:
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all()
    from gevent.pool import Pool
except ImportError:
    raise RuntimeError('cannot use gevent worker; gevent is not installed')


from ..logging import get_logger
from .base import BaseWorker


class GeventWorker(BaseWorker):
    def __init__(self, func, pool_size=100, timeout=None):
        # XXX: Is it necessary to patch all? I know we need at least, socket,
        # ssl, dns, and signal. There may be calls inside boto/botocore that
        # require more patching.
        super(GeventWorker, self).__init__(func, pool_size=pool_size,
                                           timeout=timeout)
        self.logger = get_logger(__name__)
        self.pool = Pool(size=pool_size)

    def process_messages(self, messages):
        greenlet_to_message = {}
        processed = []

        self.logger.debug('processesing %d messages', len(messages))

        for message in messages:
            try:
                g = self.pool.spawn(self.func, message)
            except:
                self.logger.exception('cannot submit jobs to pool')
                raise
            greenlet_to_message[g] = message

        for g in gevent.iwait(greenlet_to_message):
            message = greenlet_to_message[g]
            if g.successful():
                processed.append(message)
            else:
                self.logger.exception('exception processing message %s',
                                      message['MessageId'])

        return processed

    def shutdown(self):
        self.pool.join()
