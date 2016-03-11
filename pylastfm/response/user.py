import six

from figgis import Field
from pylastfm.response.common import (ApiConfig, dateparse, extract,
                                      string_or_null, _TrackBase,
                                      _ArtistBase, bool_from_int, images)


class Track(ApiConfig):

    __inherits__ = [_TrackBase]

    date = Field(extract('date', coerce=dateparse), key='@attr',
                 required=True)

    album_name = Field(extract('name'), key='album', required=True)
    album_mbid = Field(extract('mbid', coerce=string_or_null), key='album',
                       required=True)
    album_url = Field(extract('url', coerce=string_or_null), key='album',
                      required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


class User(ApiConfig):

    name = Field(six.text_type, required=True)
    realname = Field(six.text_type, required=True)
    url = Field(six.text_type, required=True)
    gender = Field(six.text_type, required=True)
    country = Field(six.text_type, required=True)
    age = Field(int, required=True)
    bootstrap = Field(int, required=True)
    playcount = Field(int, required=True)
    registered = Field(extract('#text', coerce=dateparse), required=True)
    recent_track = Field(Track, key='recenttrack')


class Artist(ApiConfig):

    __inherits__ = [_ArtistBase]

    playcount = Field(int, required=True)
    rank = Field(extract('rank', coerce=int), key='@attr', required=True)


class ChartArtist(ApiConfig):

    name = Field(six.text_type, required=True)
    mbid = Field(six.text_type)
    url = Field(six.text_type)
    playcount = Field(int, required=True)
    rank = Field(extract('rank', coerce=int), key='@attr', required=True)


class ChartAlbum(ApiConfig):

    __inherits__ = [ChartArtist]

    artist_name = Field(extract('#text'), key='artist', required=True)
    artist_mbid = Field(extract('mbid'), key='artist', required=True)


class ChartItem(ApiConfig):

    start = Field(dateparse, key='from', required=True)
    end = Field(dateparse, key='to', required=True)

    def albums(self, username=None):
        """Get a user's top albums for this date range"""
        return self._client.user.get_weekly_album_chart(username,
                                                        start=self.start,
                                                        end=self.end)

    def artists(self, username=None):
        """Get a user's top artists for this date range"""
        return self._client.user.get_weekly_artist_chart(username,
                                                         start=self.start,
                                                         end=self.end)

    def tracks(self, username=None):
        """Get a user's top tracks for this date range"""
        return self._client.user.get_weekly_track_chart(username,
                                                        start=self.start,
                                                        end=self.end)


class ChartTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    rank = Field(extract('rank', coerce=int), key='@attr', required=True)
    artist_name = Field(extract('#text'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)


class RecentTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    streamable = Field(bool_from_int, required=True)

    album_name = Field(extract('#text'), key='album', required=True)
    album_mbid = Field(extract('mbid', coerce=string_or_null), key='album',
                       required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')
    artist_images = Field(extract('image', coerce=images), default=[],
                          key='artist')

    loved = Field(bool_from_int, required=True)


class ArtistTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    streamable = Field(bool_from_int, required=True)

    album_name = Field(extract('#text'), key='album', required=True)
    album_mbid = Field(extract('mbid', coerce=string_or_null), key='album',
                       required=True)

    artist_name = Field(extract('#text'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')
