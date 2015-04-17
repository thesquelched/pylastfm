import six
from lastfm.util import PaginatedIterator

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
            make_paginated({'collection': [2 * i, 2 * i + 1]}, i + 1, 3, 6)
            for i in range(3)]

        resp = client._paginate_request('GET', 'method', 'collection')

        assert request.call_count == 1
        assert 'collection' in resp

        coll = resp['collection']
        assert isinstance(coll, PaginatedIterator)
        assert coll.pages == 3
        assert len(coll) == 6
        assert list(coll) == list(range(6))

        assert request.call_count == 3
