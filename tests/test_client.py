import pytest
import six
from pylastfm.util import PaginatedIterator
from pylastfm.auth import (Password, PasswordAuthToken, SessionKeyFile,
                           SessionKey)
from pylastfm import LastFM

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def make_paginated(response, page, total_pages, total):
    result = response.copy()
    result.update({
        '@attr': {
            'page': six.text_type(page),
            'totalPages': six.text_type(total_pages),
            'total': six.text_type(total),
        }
    })
    return result


def test_pagination(client):
    with patch.object(client, '_request') as request:
        request.side_effect = [
            make_paginated({'coll': [0, 1]}, 1, 3, 6)
        ] + [[2 * i, 2 * i + 1] for i in range(1, 3)]

        resp = client._paginate_request('GET', 'method', 'coll')

        assert request.call_count == 1
        assert 'coll' in resp

        coll = resp['coll']
        assert isinstance(coll, PaginatedIterator)
        assert coll.pages == 3
        assert len(coll) == 6
        assert list(coll) == list(range(6))

        assert request.call_count == 3


@pytest.mark.parametrize('auth_method,session_key,auth_class', [
    ('password', None, Password),
    ('hashed_password', None, PasswordAuthToken),
    ('session_key', None, SessionKey),
    ('session_key_file', None, SessionKeyFile),
    (None, 'session_key', SessionKey),
    (None, __file__, SessionKeyFile),
    (None, None, Password),
])
def test_auth_method(auth_method, session_key, auth_class):
    client = LastFM('key', 'secret', username='username', password='password',
                    auth_method=auth_method, session_key=session_key)
    assert isinstance(client._auth, auth_class)


def test_session_key_auth():
    auth = SessionKey('key', 'secret', 'username', 'password', 'session_key')
    assert auth.session_key() == 'session_key'
