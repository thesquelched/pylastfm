import six
import pytest

from pylastfm.response import common
from pylastfm.util import PaginatedIterator


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_artists(client, limit_one):
    resp = client.library.get_artists('rj',
                                      limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    album = six.next(resp)
    assert isinstance(album, common.LibraryArtist)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)
