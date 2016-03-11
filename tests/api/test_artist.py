import six
import pytest

from pylastfm.response import common
from pylastfm.util import PaginatedIterator


@pytest.mark.live
def test_get_correction(client):
    resp = client.artist.get_correction('queene')
    assert isinstance(resp, list)
    assert all(isinstance(item, common.CorrectedArtist) for item in resp)


@pytest.mark.live
def test_get_info(client):
    artist = client.artist.get_info('Queen')
    assert isinstance(artist, common.Artist)


@pytest.mark.live
def test_get_similar(client):
    resp = client.artist.get_similar('queen')
    assert isinstance(resp, list)
    assert all(isinstance(item, common.SimilarArtist) for item in resp)


@pytest.mark.live
def test_get_tags(client):
    resp = client.artist.get_tags('queen')
    assert isinstance(resp, list)
    assert all(isinstance(item, common.Tag) for item in resp)


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_albums(client, limit_one):
    resp = client.artist.get_top_albums('Queen',
                                        limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    album = six.next(resp)
    assert isinstance(album, common.Album)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)


@pytest.mark.live
def test_get_top_tags(client):
    resp = client.artist.get_top_tags('Queen')
    assert isinstance(resp, list)
    assert all(isinstance(item, common.Tag) for item in resp)


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_tracks(client, limit_one):
    resp = client.artist.get_top_tracks('Queen',
                                        limit=1 if limit_one else None)

    assert isinstance(resp, PaginatedIterator)

    track = six.next(resp)
    assert isinstance(track, common.TopTrack)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_search(client, limit_one):
    resp = client.artist.search('Queen', limit=1 if limit_one else None)

    assert isinstance(resp, PaginatedIterator)

    artist = six.next(resp)
    assert isinstance(artist, common.SearchArtist)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)
