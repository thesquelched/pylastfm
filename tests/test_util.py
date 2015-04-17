import pytest
from mock import MagicMock

from lastfm.util import Signer
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
