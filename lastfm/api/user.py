class UserAPI(object):

    def __init__(self, client):
        self._client = client

    def get_artist_tracks(self, user, artist, start=None, end=None):
        """
        Get artist tracks scrobbled by the user
        """
        return self._client._paginate_request(
            'GET',
            'user.getArtistTracks',
            'track',
            unwrap='artisttracks',
            params=dict(user=user,
                        artist=artist,
                        start=start,
                        end=end)
        )
