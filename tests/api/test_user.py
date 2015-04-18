import pytest

from lastfm.response.common import ArtistTrack, Track, RecentTrack


@pytest.mark.live
def test_artist_tracks(client):
    track = next(client.user.get_artist_tracks('rj', 'metallica'))
    assert isinstance(track, ArtistTrack)


@pytest.mark.live
def test_banned_tracks(client):
    track = next(client.user.get_banned_tracks('rj'))
    assert isinstance(track, Track)


@pytest.mark.live
def test_loved_tracks(client):
    track = next(client.user.get_loved_tracks('rj'))
    assert isinstance(track, Track)


@pytest.mark.live
def test_recent_tracks(client):
    track = next(client.user.get_recent_tracks('rj'))
    assert isinstance(track, RecentTrack)
