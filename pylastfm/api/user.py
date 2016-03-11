from pylastfm.api.api import API
from pylastfm.response import common
from pylastfm.response.user import (User, Artist, ChartAlbum, ChartArtist,
                                    ChartItem, ChartTrack)
from pylastfm.util import query_date


VALID_PERIODS = frozenset(['overall', '7day', '1month', '3month', '6month',
                           '12month'])


class Resource(API):

    def get_artist_tracks(self, username, artist, start=None, end=None):
        """
        Get artist tracks scrobbled by the user

        http://www.last.fm/api/show/user.getArtistTracks
        """
        resp = self._client._paginate_request(
            'GET',
            'user.getArtistTracks',
            'track',
            params=dict(
                user=username,
                artist=artist,
                start=query_date(start),
                end=query_date(end)
            ),
            unwrap='artisttracks',
        )['track']
        return self.model_iterator(common.ArtistTrack, resp)

    def get_friends(self, username, recent_track=False):
        """
        Get a list of the user's friends on Last.fm.

        http://www.last.fm/api/show/user.getFriends
        """
        resp = self._client._paginate_request(
            'GET',
            'user.getFriends',
            'user',
            params=dict(
                user=username,
                recenttracks=int(recent_track)
            ),
            unwrap='friends',
        )['user']

        return self.model_iterator(User, resp)

    def get_info(self, username=None):
        """
        Get information about a user profile.

        http://www.last.fm/api/show/user.getInfo
        """
        resp = self._client._request(
            'GET',
            'user.getInfo',
            params=dict(
                user=username or self._client.username,
            ),
            unwrap='user',
        )
        return self.model(User, resp)

    def get_loved_tracks(self, username):
        """
        Get tracks loved by the user.

        http://www.last.fm/api/show/user.getLovedTracks
        """
        resp = self._client._paginate_request(
            'GET',
            'user.getLovedTracks',
            'track',
            unwrap='lovedtracks',
            params=dict(user=username),
        )
        return self.model_iterator(common.Track, resp['track'])

    def _get_personal_tags(self, username, tag, tag_type):
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
            '{0}.{1}'.format(coll_name, tag_type),
            unwrap='taggings',
            params=dict(user=username, tag=tag, taggingtype=tag_type),
        )[coll_name][tag_type]

    def get_artist_tags(self, username, tag):
        """
        Get the user's personal artist tags.

        http://www.last.fm/api/show/user.getPersonalTags
        """
        resp = self._get_personal_tags(username, tag, 'artist')

        return self.model_iterator(common.TagArtist, resp)

    def get_album_tags(self, username, tag):
        """
        Get the user's personal album tags.

        http://www.last.fm/api/show/user.getPersonalTags
        """
        resp = self._get_personal_tags(username, tag, 'album')

        return self.model_iterator(common.TagAlbum, resp)

    def get_track_tags(self, username, tag):
        """
        Get the user's personal track tags.

        http://www.last.fm/api/show/user.getPersonalTags
        """
        resp = self._get_personal_tags(username, tag, 'track')

        return self.model_iterator(common.TagTrack, resp)

    def get_recent_tracks(self, username, start=None, end=None):
        """
        Get tracks recently played by the user. Always returns extended data.

        http://www.last.fm/api/show/user.getRecentTracks
        """
        resp = self._client._paginate_request(
            'GET',
            'user.getRecentTracks',
            'track',
            params={
                'user': username,
                'from': query_date(start),
                'to': query_date(end),
                'extended': 1
            },
            unwrap='recenttracks',
        )['track']
        return self.model_iterator(common.RecentTrack, resp)

    def get_top_albums(self, username=None, period=None, limit=None):
        """
        Get the top albums listened to by a user. Valid periods are 'overall',
        '7day', '1month', '3month', '6month', and '12month' (default:
        'overall').

        http://www.last.fm/api/show/user.getTopAlbums
        """
        if period is not None and period not in VALID_PERIODS:
            raise ValueError('Invalid period: {0}'.format(period))

        perpage = min(30, limit) if limit else 30

        resp = self._client._paginate_request(
            'GET',
            'user.getTopAlbums',
            'album',
            params=dict(
                user=username or self._client.username,
                period=period
            ),
            limit=limit,
            perpage=perpage,
            unwrap='topalbums',
        )['album']

        return self.model_iterator(common.Album, resp)

    def get_top_artists(self, username=None, period=None, limit=None):
        """
        Get the top artists lsitened to by a user. Valid periods are 'overall',
        '7day', '1month', '3month', '6month', and '12month' (default:
        'overall').

        http://www.last.fm/api/show/user.getTopArtists
        """
        if period is not None and period not in VALID_PERIODS:
            raise ValueError('Invalid period: {0}'.format(period))

        perpage = min(30, limit) if limit else 30

        resp = self._client._paginate_request(
            'GET',
            'user.getTopArtists',
            'artist',
            params=dict(
                user=username or self._client.username,
                period=period
            ),
            limit=limit,
            perpage=perpage,
            unwrap='topartists',
        )['artist']

        return self.model_iterator(Artist, resp)

    def get_top_tags(self, username=None):
        """
        Get the top tags used by this user.  Note that this is currently
        broken in the API.

        http://www.last.fm/api/show/user.getTopTags
        """
        return self._client._request(
            'GET',
            'user.getTopTags',
            params=dict(
                user=username or self._client.username,
            ),
            unwrap='toptags',
        )['tag']

    def get_top_tracks(self, username=None, period=None, limit=None):
        """
        Get the top tracks listened to by a user. Valid periods are 'overall',
        '7day', '1month', '3month', '6month', and '12month' (default:
        'overall').

        http://www.last.fm/api/show/user.getTopTracks
        """
        if period is not None and period not in VALID_PERIODS:
            raise ValueError('Invalid period: {0}'.format(period))

        perpage = min(30, limit) if limit else 30

        resp = self._client._paginate_request(
            'GET',
            'user.getTopTracks',
            'track',
            params=dict(
                user=username or self._client.username,
                period=period,
            ),
            limit=limit,
            perpage=perpage,
            unwrap='toptracks',
        )['track']

        return self.model_iterator(common.TagTrack, resp)

    def get_weekly_album_chart(self, username, start=None, end=None):
        """
        Get an album chart for a user profile, for a given date range. If no
        date range is supplied, it will return the most recent album chart for
        this user.

        http://www.last.fm/api/show/user.getWeeklyAlbumChart
        """
        resp = self._client._request(
            'GET',
            'user.getWeeklyAlbumChart',
            unwrap='weeklyalbumchart',
            params={
                'user': username,
                'from': query_date(start),
                'to': query_date(end)
            },
        )['album']

        return [self.model(ChartAlbum, item) for item in resp]

    def get_weekly_artist_chart(self, username, start=None, end=None):
        """
        Get an artist chart for a user profile, for a given date range. If no
        date range is supplied, it will return the most recent artist chart for
        this user.

        http://www.last.fm/api/show/user.getWeeklyArtistChart
        """
        resp = self._client._request(
            'GET',
            'user.getWeeklyArtistChart',
            unwrap='weeklyartistchart',
            params={'user': username,
                    'from': query_date(start),
                    'to': query_date(end)},
        )['artist']

        return [self.model(ChartArtist, item) for item in resp]

    def get_weekly_chart_list(self, username):
        """
        Get a list of available charts for this user, expressed as date ranges
        which can be sent to the chart services

        http://www.last.fm/api/show/user.getWeeklyChartList
        """
        resp = self._client._request(
            'GET',
            'user.getWeeklyChartList',
            unwrap='weeklychartlist',
            params=dict(user=username),
        )['chart']

        return [self.model(ChartItem, item) for item in resp]

    def get_weekly_track_chart(self, username, start=None, end=None):
        """
        Get an track chart for a user profile, for a given date range. If no
        date range is supplied, it will return the most recent track chart for
        this user.

        http://www.last.fm/api/show/user.getWeeklyTrackChart
        """
        resp = self._client._request(
            'GET',
            'user.getWeeklyTrackChart',
            params={
                'user': username,
                'from': query_date(start),
                'to': query_date(end)
            },
            unwrap='weeklytrackchart',
        )['track']

        return [self.model(ChartTrack, item) for item in resp]
