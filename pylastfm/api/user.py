from pylastfm.api.api import API
from pylastfm.response.common import ArtistTrack, Track, RecentTrack
from pylastfm.util import query_date


VALID_PERIODS = frozenset(['overall', '7day', '1month', '3month', '6month',
                           '12month'])


class User(API):

    def get_artist_tracks(self, user, artist, start=None, end=None):
        """
        Get artist tracks scrobbled by the user

        http://www.last.fm/api/show/user.getArtistTracks
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

    def get_friends(self, user, recent_tracks=False):
        """
        Get a list of the user's friends on Last.fm.

        http://www.last.fm/api/show/user.getFriends
        """
        return self._client._paginate_request(
            'GET',
            'user.getFriends',
            'user',
            unwrap='friends',
            params=dict(user=user, recenttracks=int(recent_tracks)),
        )['user']

    def get_info(self, user):
        """
        Get information about a user profile.

        http://www.last.fm/api/show/user.getInfo
        """
        return self._client._request(
            'GET',
            'user.getInfo',
            unwrap='user',
            params=dict(user=user),
        )

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

    def get_personal_tags(self, user, tag, tag_type):
        """
        Get the user's personal tags. Tag type must be either 'artist',
        'album', or 'track'.

        http://www.last.fm/api/show/user.getPersonalTags
        """
        if tag_type not in ('artist', 'album', 'track'):
            raise ValueError('Invalid tag type: {0}'.format(tag_type))

        coll_name = tag_type + 's'
        return self._client._paginate_request(
            'GET',
            'user.getPersonalTags',
            coll_name,
            unwrap='taggings',
            params=dict(user=user, tag=tag, taggingtype=tag_type),
        )[coll_name]

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

    def get_top_albums(self, user, period=None):
        """
        Get the top albums listened to by a user. Valid periods are 'overall',
        '7day', '1month', '3month', '6month', and '12month' (default:
        'overall').

        http://www.last.fm/api/show/user.getTopAlbums
        """
        if period is not None and period not in VALID_PERIODS:
            raise ValueError('Invalid period: {0}'.format(period))

        return self._client._paginate_request(
            'GET',
            'user.getTopAlbums',
            'album',
            unwrap='topalbums',
            params=dict(user=user, period=period),
        )['album']

    def get_top_artists(self, user, period=None):
        """
        Get the top artists lsitened to by a user. Valid periods are 'overall',
        '7day', '1month', '3month', '6month', and '12month' (default:
        'overall').

        http://www.last.fm/api/show/user.getTopArtists
        """
        if period is not None and period not in VALID_PERIODS:
            raise ValueError('Invalid period: {0}'.format(period))

        return self._client._paginate_request(
            'GET',
            'user.getTopArtists',
            'artist',
            unwrap='topartists',
            params=dict(user=user, period=period),
        )['artist']

    def get_top_tags(self, user):
        """
        Get the top tags used by this user.

        http://www.last.fm/api/show/user.getTopTags
        """
        return self._client._request(
            'GET',
            'user.getTopTags',
            unwrap='toptags',
            params=dict(user=user),
        )['tag']

    def get_top_tracks(self, user, period=None):
        """
        Get the top tracks listened to by a user. Valid periods are 'overall',
        '7day', '1month', '3month', '6month', and '12month' (default:
        'overall').

        http://www.last.fm/api/show/user.getTopTracks
        """
        if period is not None and period not in VALID_PERIODS:
            raise ValueError('Invalid period: {0}'.format(period))

        return self._client._paginate_request(
            'GET',
            'user.getTopTracks',
            'track',
            unwrap='toptracks',
            params=dict(user=user, period=period),
        )['track']

    def get_weekly_album_chart(self, user, start=None, end=None):
        """
        Get an album chart for a user profile, for a given date range. If no
        date range is supplied, it will return the most recent album chart for
        this user.

        http://www.last.fm/api/show/user.getWeeklyAlbumChart
        """
        return self._client._request(
            'GET',
            'user.getWeeklyAlbumChart',
            unwrap='weeklyalbumchart',
            params={'user': user,
                    'from': query_date(start),
                    'to': query_date(end)},
        )['album']

    def get_weekly_artist_chart(self, user, start=None, end=None):
        """
        Get an artist chart for a user profile, for a given date range. If no
        date range is supplied, it will return the most recent artist chart for
        this user.

        http://www.last.fm/api/show/user.getWeeklyArtistChart
        """
        return self._client._request(
            'GET',
            'user.getWeeklyArtistChart',
            unwrap='weeklyartistchart',
            params={'user': user,
                    'from': query_date(start),
                    'to': query_date(end)},
        )['artist']

    def get_weekly_chart_list(self, user):
        """
        Get a list of available charts for this user, expressed as date ranges
        which can be sent to the chart services

        http://www.last.fm/api/show/user.getWeeklyChartList
        """
        return self._client._request(
            'GET',
            'user.getWeeklyChartList',
            unwrap='weeklychartlist',
            params=dict(user=user),
        )['chart']

    def get_weekly_track_chart(self, user, start=None, end=None):
        """
        Get an track chart for a user profile, for a given date range. If no
        date range is supplied, it will return the most recent track chart for
        this user.

        http://www.last.fm/api/show/user.getWeeklyTrackChart
        """
        return self._client._request(
            'GET',
            'user.getWeeklyTrackChart',
            unwrap='weeklytrackchart',
            params={'user': user,
                    'from': query_date(start),
                    'to': query_date(end)},
        )['track']
