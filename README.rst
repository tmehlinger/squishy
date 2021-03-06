Squishy
=======

.. image:: https://circleci.com/gh/tmehlinger/squishy/tree/master.svg?style=shield
    :target: https://circleci.com/gh/tmehlinger/squishy/tree/master
.. image:: https://coveralls.io/repos/github/tmehlinger/squishy/badge.svg?branch=master
    :target: https://coveralls.io/github/tmehlinger/squishy?branch=master


Squishy is a simple Amazon SQS consumer for Python. Many versions of Python
are supported, including 2.7, 3.3, 3.4, and 3.5. 2.6 should work but it is
untested and unsupported.

This is currently *beta* software! It has a suite of tests and it's being used
for non-critical production tasks but it is still very young software.


Installing
----------

Install from pypi: ``pip install squishy``


Developing
----------

* Create a virtualenv.
* Clone the repo.
* Install the requirements. If you want to use the futures workers on Python
  2.7, be sure to install `futures <https://pypi.python.org/pypi/futures>`_.
* Run ``python setup.py develop`` to get the ``squishy`` CLI tool.


Using
-----

Squishy provides a CLI to run a worker that will dispatch messages to a
callback you define. The callback should accept a single parameter
representing a single message consumed from an SQS queue. The message will be
an instance of `SQS.Message <http://boto3.readthedocs.io/en/latest/reference/services/sqs.html#message>`_.

Example:

.. code-block:: python

    # my_consumer.py

    def my_callback(message):
        print('Got a message! Contents:', message.body)

Then on the command line:

``$ squishy run_consumer https://sqs.us-east-1.amazonaws.com/12345/my_queue my_consumer:my_callback``


Authentication
--------------

Squishy uses boto3, which will automatically load credentials from
``$HOME/.aws/credentials``. If you need more control over authentication, you can
give Squishy a factory function for creating a custom session.


CLI reference
-------------

::

    $ squishy --help
    Usage: squishy [OPTIONS] COMMAND [ARGS]...

    Options:
      --log-level [debug|info|warning|error|critical]
                                      Logging level.
      --botocore-log-level [debug|info|warning|error|critical]
                                      botocore logging level.
      --version                       Show the version and exit.
      --help                          Show this message and exit.

    Commands:
      run_consumer


    $ squishy run_consumer --help
    Usage: squishy run_consumer [OPTIONS] QUEUE_URL CALLBACK

    Options:
      --session-factory TEXT          Factory function for a custom boto3.Session.
      -c, --concurrency INTEGER       Worker concurrency.
      -m, --polling-method [long|short]
                                      Polling method.
      -t, --polling-timeout INTEGER   Polling interval in seconds.
      -n, --polling-count INTEGER     Number of messages to fetch when polling.
      -w, --worker-class [futures_process|futures_thread|gevent|mp_process|mp_thread]
                                      Worker class.
      --help                          Show this message and exit.


Examples
--------

Using Squishy to submit tasks to Celery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Callback code:

.. code-block:: python

    # squishy_celery.py

    import logging
    import os

    from celery import Celery


    log = logging.getLogger(__name__)


    class MySquishyCallback(object):
        def __init__(self, broker_url, task_name):
            self.celery_app = Celery(__name__, broker=broker_url)
            self.task_name = task_name

        def __call__(self, message):
            log.info('received a message!')
            body = message.body
            self.celery_app.send_task(self.task_name, args=(body,))

    callback = MySquishyCallback(os.environ['MY_BROKER_URL'], 'my.celery.task')


Starting the consumer:

    ``$ squishy run_consumer https://sqs.us-east-1.amazonaws.com/12345/my_queue squishy_celery:callback``
