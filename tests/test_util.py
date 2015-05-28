import pytest
from mock import MagicMock

from lastfm.util import Signer, nested_set, nested_get, nested_in
from lastfm.client import ApiInfo


@pytest.fixture
def mock_client():
    return MagicMock(
        api_info=ApiInfo(url='url',
                         key='key',
                         secret='secret')
    )


@pytest.fixture
def session_client():
    return MagicMock(
        api_info=ApiInfo(url='url',
                         key='key',
                         secret='secret',
                         session_key='session')
    )


def test_signer(mock_client):
    signer = Signer(mock_client)

    assert signer.sign() == '5ebe2294ecd0e0f08eab7690d2a6ee69'

    params = dict(key1='value1', key2='value2')
    assert signer.sign(**params) == 'ecf65eec6fbed7f76fd01d716e797889'


def test_signer_sessionkey(session_client):
    signer = Signer(session_client)

    params = dict(key1='value1', key2='value2')
    assert signer.sign(**params) == '67ef41ef61987d760758cdb771a57064'


def test_nested_get():
    baz = 1
    bar = {'baz': baz}
    foo = {'bar': bar}
    data = {'foo': foo}

    assert nested_get(data, []) == data
    assert nested_get(data, ['foo']) == foo
    assert nested_get(data, ['foo', 'bar']) == bar
    assert nested_get(data, ['foo', 'bar', 'baz']) == baz

    assert nested_get({}, ['foo',  'bar'], default=None) is None

    pytest.raises(KeyError, nested_get, {}, ['foo'])


@pytest.mark.parametrize('keys,data,updated', [
    (['foo'], {}, {'foo': 'set'}),
    (['foo'], {'foo': 1}, {'foo': 'set'}),
    (['foo', 'bar'], {'foo': {'bar': 1}}, {'foo': {'bar': 'set'}}),
])
def test_nested_set(keys, data, updated):
    nested_set(data, keys, 'set')
    assert data == updated


def test_nested_set_fail():
    pytest.raises(KeyError, nested_set, {}, ['foo', 'bar'], 1)


@pytest.mark.parametrize('keys,data,is_in', [
    (['foo'], {}, False),
    (['foo'], {'foo': 1}, True),
    (['foo'], {'foo': {'bar': None}}, True),
    (['foo', 'bar'], {'foo': {'bar': None}}, True),
    (['foo', 'bar', 'baz'], {'foo': {'bar': {}}}, False),
])
def test_nested_in(keys, data, is_in):
    assert nested_in(data, keys) == is_in
