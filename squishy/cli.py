from __future__ import absolute_import

import importlib
import logging
import sys

import click

from . import __version__
from .consumer import SqsConsumer
from .logging import get_logger
from .workers import WORKER_CLASSES


FORMAT = '[%(asctime)s] [%(levelname)s/%(name)s] %(message)s'

LOG_CHOICES = click.Choice(['debug', 'info', 'warning', 'error', 'critical'])
WORKER_CHOICES = click.Choice(sorted(WORKER_CLASSES.keys()))


if sys.version_info[0] == 3:
    DEFAULT_WORKER = 'futures_thread'
else:
    DEFAULT_WORKER = 'mp_thread'


def get_log_level(ctx, param, value):
    return getattr(logging, value.upper())


def import_callable(ctx, param, value):
    if value is None:
        return None

    delim = ':'
    if delim not in value:
        raise click.BadParameter(
            'string to import should have the form '
            'pkg.module:callable_attribute')

    mod, identifier = value.rsplit(delim, 1)

    try:
        func_or_cls = getattr(importlib.import_module(mod), identifier)
    except AttributeError:
        raise click.BadParameter('{} does not exist in {}'
                                 .format(identifier, mod))

    if callable(func_or_cls):
        return func_or_cls
    raise RuntimeError('{} is not callable'.format(value))


def import_worker(ctx, param, value):
    importable = WORKER_CLASSES[value]
    if value == 'gevent':
        import gevent.monkey
        gevent.monkey.patch_socket()
        gevent.monkey.patch_ssl()
    return import_callable(ctx, param, importable)


@click.group()
@click.option('--log-level', default='warning',
              type=LOG_CHOICES, callback=get_log_level,
              help='Logging level.')
@click.option('--botocore-log-level', default='critical',
              type=LOG_CHOICES, callback=get_log_level,
              help='botocore logging level.')
@click.version_option(version=__version__)
def cli(log_level, botocore_log_level):
    logging.basicConfig(level=log_level, format=FORMAT)
    logging.getLogger('botocore').setLevel(botocore_log_level)


@cli.command()
@click.argument('queue_url')
@click.argument('callback', callback=import_callable)
@click.option('--session-factory', type=str, callback=import_callable,
              help='Factory function for a custom boto3.Session.')
@click.option('-c', '--concurrency', default=8, type=int,
              help='Worker concurrency.')
@click.option('-m', '--polling-method', default='long',
              type=click.Choice(['long', 'short']), help='Polling method.')
@click.option('-t', '--polling-timeout', default=20,
              help='Polling interval in seconds.')
@click.option('-n', '--polling-count', default=10,
              help='Number of messages to fetch when polling.')
@click.option('-w', '--worker-class', default=DEFAULT_WORKER,
              type=WORKER_CHOICES, callback=import_worker,
              help='Worker class.')
def run_consumer(queue_url, callback, session_factory=None, **kw):
    if session_factory:
        kw['session'] = session_factory()

    short = kw.pop('polling_method') == 'short'
    worker_cls = kw.pop('worker_class')

    worker = worker_cls(callback, pool_size=kw.pop('concurrency'))

    get_logger(__name__).info('using worker class %s', worker_cls.__name__)

    consumer = SqsConsumer(queue_url, use_short_polling=short, worker=worker,
                           **kw)
    consumer.run()


def main():
    # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
    cli(obj={})


if __name__ == '__main__':
    main()
