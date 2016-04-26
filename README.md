# Squishy

Squishy is a simple Amazon SQS consumer for Python. Many versions of Python
are (or will be) supported.

This is currently *alpha* software! It works under basic testing but does not
yet have a full battery of automated tests. Use at your own risk!


## Installing

Currently, you have to clone the repo and install the hard way. This will
change soon.

* Clone the repo.
* Install the requirements. If you want to use the futures workers on Python
  2, be sure to install `futures`.
* `python setup.py install`


## Using

Squishy provides a CLI to run a worker that will dispatch messages to a
callback you define. The callback should accept a single parameter
representing a single message consumed from an SQS queue.

Example:

```python
# my_consumer.py

def my_callback(message):
    print('Got a message! Contents:', message)
```

Then on the command line:

`$ squishy run_consumer https://sqs.us-east-1.amazonaws.com/12345/my_queue my_consumer:my_callback`


## Authentication

Squishy uses boto3, which will automatically load credentials from
`$HOME/.aws/credentials`. If you need more control over authentication, you can
give Squishy a factory function for creating a custom session.
