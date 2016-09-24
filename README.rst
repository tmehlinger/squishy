Squishy
=======

.. image:: https://circleci.com/gh/tmehlinger/squishy/tree/master.svg?style=svg
    :target: https://circleci.com/gh/tmehlinger/squishy/tree/master

Squishy is a simple Amazon SQS consumer for Python. Many versions of Python
are supported, including 2.6, 2.7, 3.3, 3.4, and 3.5.

This is currently *beta* software! It has a suite of tests and it's being used
for non-critical production tasks but it is still very young software.


Installing
----------

Install from pypi: `pip install squishy`


Developing
----------

* Create a virtualenv.
* Clone the repo.
* Install the requirements. If you want to use the futures workers on Python
  2.6 or 2.7, be sure to install `futures <https://pypi.python.org/pypi/futures>`_.
* Run ``python setup.py develop`` to get the `squishy` CLI tool.


Using
-----

Squishy provides a CLI to run a worker that will dispatch messages to a
callback you define. The callback should accept a single parameter
representing a single message consumed from an SQS queue. The message will be
an instance of `SQS.Message <http://boto3.readthedocs.io/en/latest/reference/services/sqs.html#message>`_

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
