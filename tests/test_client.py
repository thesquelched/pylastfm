import six
from pylastfm.util import PaginatedIterator

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
