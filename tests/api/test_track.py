import pytest
import six

from lastfm.response import common
from lastfm.util import PaginatedIterator


@pytest.mark.live
def test_get_buy_links(client):
    resp = client.track.get_buy_links('Radiohead', 'Creep', 'USA')
    assert resp
    assert 'physicals' in resp
    assert 'downloads' in resp


@pytest.mark.live
def test_get_correction(client):
    resp = client.track.get_correction('guns and roses', 'Mrbrownstone')
    assert isinstance(resp, common.CorrectedTrack)


@pytest.mark.live
def test_get_fingerprint_metadata(client):
    resp = client.track.get_fingerprint_metadata('1234')
    assert resp
    assert all(isinstance(item, common.Track) for item in resp)


@pytest.mark.live
def test_get_info(client):
    resp = client.track.get_info('cher', 'believe')
    assert resp
    assert isinstance(resp, common.TrackInfo)


@pytest.mark.live
def test_get_shouts(client):
    resp = client.track.get_shouts('cher', 'believe')
    assert isinstance(resp, PaginatedIterator)

    shout = six.next(resp)
    assert shout
    assert 'body' in shout


@pytest.mark.live
def test_get_similar(client):
    resp = client.track.get_similar('cher', 'believe')
    assert resp

    track = resp[0]
    assert isinstance(track, common.Track)


@pytest.mark.live
def test_get_tags(client):
    resp = client.track.get_tags('AC/DC', 'Hells Bells', username='rj')
    assert resp

    track = resp[0]
    assert isinstance(track, common.Tag)


@pytest.mark.live
def test_get_top_fans(client):
    resp = client.track.get_top_fans('cher', 'believe')
    assert resp

    assert 'name' in resp[0]


@pytest.mark.live
def test_get_top_tags(client):
    resp = client.track.get_top_tags('radiohead', 'paranoid android')
    assert resp

    track = resp[0]
    assert isinstance(track, common.Tag)


@pytest.mark.live
@pytest.mark.parametrize('artist,limit_to_one', [
    (None, False),
    (None, True),
    ('LCD Soundsystem', False),
    ('LCD Soundsystem', True),
])
def test_search(artist, limit_to_one, client):
    resp = client.track.search('Get Innocuous!', artist=artist,
                               limit=1 if limit_to_one else None)
    assert isinstance(resp, PaginatedIterator)

    track = six.next(resp)
    assert isinstance(track, common.SearchTrack)

    if limit_to_one:
        pytest.raises(StopIteration, six.next, resp)
