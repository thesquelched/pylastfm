from lastfm.api.api import API
from lastfm.response.common import ArtistTrack, BannedTrack


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
                        start=start,
                        end=end)
        )
        return (ArtistTrack(track, client=self._client)
                for track in resp['track'])

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
        return (BannedTrack(track, client=self._client)
                for track in resp['track'])
