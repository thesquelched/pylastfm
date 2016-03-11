import six
import pytest

from pylastfm.response import common
from pylastfm.util import PaginatedIterator


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_albums(client, limit_one):
    resp = client.tag.get_top_albums('rock',
                                     limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    album = six.next(resp)
    assert isinstance(album, common.TagAlbum)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_artists(client, limit_one):
    resp = client.tag.get_top_artists('rock',
                                      limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    album = six.next(resp)
    assert isinstance(album, common.TagArtist)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)


@pytest.mark.live
def test_get_top_tags(client):
    resp = client.tag.get_top_tags()
    assert isinstance(resp, list)
    assert all(isinstance(item, common.TopTag) for item in resp)


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_tracks(client, limit_one):
    resp = client.tag.get_top_tracks('rock',
                                     limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    album = six.next(resp)
    assert isinstance(album, common.TagTrack)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)
