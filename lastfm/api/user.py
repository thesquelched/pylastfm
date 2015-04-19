from lastfm.api.api import API
from lastfm.response.common import ArtistTrack, Track, RecentTrack
from lastfm.util import query_date


class User(API):

    def get_artist_tracks(self, user, artist, start=None, end=None):
        """
        Get artist tracks scrobbled by the user
        """
        resp = self._client._paginate_request(
            'GET',
            'user.getArtistTracks',
            'track',
            unwrap='artisttracks',
            params=dict(user=user,
                        artist=artist,
                        start=query_date(start),
                        end=query_date(end))
        )
        return self.model_iterator(ArtistTrack, resp['track'])

    def get_banned_tracks(self, user):
        """
        Get tracks banned by the user.

        http://www.last.fm/api/show/user.getBannedTracks
        """
        resp = self._client._paginate_request(
            'GET',
            'user.getBannedTracks',
            'track',
            unwrap='bannedtracks',
            params=dict(user=user),
        )
        return self.model_iterator(Track, resp['track'])

    def get_loved_tracks(self, user):
        """
        Get tracks loved by the user.

        http://www.last.fm/api/show/user.getLovedTracks
        """
        resp = self._client._paginate_request(
            'GET',
            'user.getLovedTracks',
            'track',
            unwrap='lovedtracks',
            params=dict(user=user),
        )
        return self.model_iterator(Track, resp['track'])

    def get_recent_tracks(self, user, start=None, end=None):
        """
        Get tracks recently played by the user. Always returns extended data.

        http://www.last.fm/api/show/user.getRecentTracks
        """
        resp = self._client._paginate_request(
            'GET',
            'user.getRecentTracks',
            'track',
            unwrap='recenttracks',
            params={'user': user,
                    'from': query_date(start),
                    'to': query_date(end),
                    'extended': 1},
        )
        return self.model_iterator(RecentTrack, resp['track'])
