import six
import pytest

from pylastfm.response.common import ArtistTrack, Track, RecentTrack
from pylastfm.response.user import User
from pylastfm.util import PaginatedIterator


@pytest.mark.live
def test_artist_tracks(client):
    track = next(client.user.get_artist_tracks('rj', 'metallica'))
    assert isinstance(track, ArtistTrack)


@pytest.mark.live
def test_loved_tracks(client):
    track = next(client.user.get_loved_tracks('rj'))
    assert isinstance(track, Track)


@pytest.mark.live
def test_recent_tracks(client):
    track = next(client.user.get_recent_tracks('rj'))
    assert isinstance(track, RecentTrack)


@pytest.mark.live
@pytest.mark.parametrize('recent_track', [False, True])
def test_get_friends(client, recent_track):
    resp = client.user.get_friends('rj', recent_track=recent_track)
    assert isinstance(resp, PaginatedIterator)
    assert isinstance(six.next(resp), User)


@pytest.mark.live
def test_get_info(client):
    resp = client.user.get_info('rj')
    assert resp
    assert 'name' in resp
    assert resp['name'] == 'RJ'


@pytest.mark.live
def get_new_releases(client):
    assert isinstance(client.user.get_friends('rj'), list)
    assert isinstance(client.user.get_friends('rj', recommendations=True),
                      list)


@pytest.mark.live
def get_past_events(client):
    assert isinstance(client.user.get_past_events('rj'), PaginatedIterator)


@pytest.mark.live
def test_get_artist_tags(client):
    assert isinstance(client.user.get_artist_tags('rj', 'rock'),
                      PaginatedIterator)


@pytest.mark.live
def test_get_album_tags(client):
    assert isinstance(client.user.get_album_tags('rj', 'rock'),
                      PaginatedIterator)


@pytest.mark.live
def test_get_track_tags(client):
    assert isinstance(client.user.get_track_tags('rj', 'rock'),
                      PaginatedIterator)


@pytest.mark.live
def test_get_top_albums(client):
    pytest.raises(ValueError, client.user.get_top_albums, 'rj', period='foo')
    assert isinstance(client.user.get_top_albums('rj'), PaginatedIterator)
    assert isinstance(client.user.get_top_albums('rj', period='7day'),
                      PaginatedIterator)


@pytest.mark.live
def test_get_top_artists(client):
    pytest.raises(ValueError, client.user.get_top_artists, 'rj', period='foo')
    assert isinstance(client.user.get_top_artists('rj'), PaginatedIterator)
    assert isinstance(client.user.get_top_artists('rj', period='7day'),
                      PaginatedIterator)


@pytest.mark.live
def test_get_top_tags(client):
    assert isinstance(client.user.get_top_tags('rj'), list)


@pytest.mark.live
def test_get_top_tracks(client):
    pytest.raises(ValueError, client.user.get_top_tracks, 'rj', period='foo')
    assert isinstance(client.user.get_top_tracks('rj'), PaginatedIterator)
    assert isinstance(client.user.get_top_tracks('rj', period='7day'),
                      PaginatedIterator)


@pytest.mark.live
def test_get_weekly_album_chart(client):
    assert isinstance(client.user.get_weekly_album_chart('rj'), list)


@pytest.mark.live
def test_get_weekly_artist_chart(client):
    assert isinstance(client.user.get_weekly_artist_chart('rj'), list)


@pytest.mark.live
def test_get_weekly_chart_list(client):
    assert isinstance(client.user.get_weekly_chart_list('rj'), list)


@pytest.mark.live
def test_get_weekly_track_chart(client):
    assert isinstance(client.user.get_weekly_track_chart('rj'), list)
