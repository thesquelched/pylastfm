import six
import pytest

from pylastfm.response import geo
from pylastfm.util import PaginatedIterator


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_artists(client, limit_one):
    resp = client.geo.get_top_artists('us',
                                      limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    album = six.next(resp)
    assert isinstance(album, geo.Artist)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_tracks(client, limit_one):
    resp = client.geo.get_top_tracks('us',
                                     limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    album = six.next(resp)
    assert isinstance(album, geo.Track)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)
