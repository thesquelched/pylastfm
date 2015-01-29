import pytest

from lastfm.util import Signer
from lastfm.client import ApiInfo


@pytest.fixture
def api_info():
    return ApiInfo(
        url='url',
        key='key',
        secret='secret',
        session_key=None)


def test_signer(api_info):
    signer = Signer(api_info)

    assert signer.sign() == '5ebe2294ecd0e0f08eab7690d2a6ee69'

    params = dict(key1='value1', key2='value2')
    assert signer.sign(**params) == 'ecf65eec6fbed7f76fd01d716e797889'


def test_signer_sessionkey(api_info):
    signer = Signer(api_info.add_session_key('session'))

    params = dict(key1='value1', key2='value2')
    assert signer.sign(**params) == '67ef41ef61987d760758cdb771a57064'
