import logging

import click
from click.testing import CliRunner
import mock
import pytest

from squishy import cli
from squishy.consumer import SqsConsumer
from squishy.noop import noop_callback
from squishy.workers.noop import NoopWorker


def test_get_log_level():
    for level in cli.LOG_CHOICES.choices:
        assert (cli.get_log_level(None, None, level) ==
                getattr(logging, level.upper()))


def test_import_callable_func():
    func = cli.import_callable(None, None, 'squishy.noop:noop_callback')
    assert callable(func)
    assert func(None) is None


def test_import_callable_object():
    obj = cli.import_callable(None, None, 'squishy.noop:noop_callback_obj')
    assert callable(obj)
    assert obj(None) is None


@pytest.mark.parametrize('spec', [
    'not_importable',
    'not.importable',
])
def test_import_callable_invalid_import_spec(spec):
    with pytest.raises(click.BadParameter) as e:
        cli.import_callable(None, None, spec)
    assert 'string to import' in e.value.args[0]


def test_import_callable_no_attribute():
    with pytest.raises(click.BadParameter) as e:
        cli.import_callable(None, None, 'squishy.noop:missing_attribute')
    assert 'does not exist' in e.value.args[0]


def test_import_callable_attribute_is_not_callable():
    with pytest.raises(RuntimeError) as e:
        cli.import_callable(None, None, 'squishy.noop:noop_dummy')
    assert 'is not callable' in e.value.args[0]


def test_import_callable_none_value():
    assert cli.import_callable(None, None, None) is None


def test_import_worker():
    func = cli.import_worker(None, None, 'futures_process')
    assert callable(func)


def test_import_gevent_worker():
    import gevent.monkey
    with mock.patch('gevent.monkey', spec=gevent.monkey) as m:
        func = cli.import_worker(None, None, 'gevent')
        assert callable(func)
        assert len(m.patch_socket.mock_calls) == 1
        assert len(m.patch_ssl.mock_calls) == 1


@mock.patch('squishy.cli.SqsConsumer', spec=SqsConsumer)
@mock.patch('squishy.workers.noop.NoopWorker', spec=NoopWorker)
def test_run_consumer(w_mock, c_mock):
    url = 'https://localhost/test/url'
    callback = 'squishy.noop:noop_callback'
    worker = 'noop'

    runner = CliRunner()
    result = runner.invoke(cli.run_consumer,
                           [url, callback, '--worker-class', worker])

    assert result.exit_code == 0

    consumer_calls = [
        mock.call(url, use_short_polling=False, worker=w_mock.return_value,
                  polling_timeout=20, polling_count=10),
        mock.call().run(),
    ]
    assert c_mock.mock_calls == consumer_calls
    assert w_mock.mock_calls[0] == mock.call(noop_callback, pool_size=8)
