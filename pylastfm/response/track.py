import six
from figgis import Config, Field
from pylastfm.response.common import (ApiConfig, extract, _TrackBase,
                                      string_or_null, bool_from_int, Wiki,
                                      images, Tag)
from pylastfm.util import query_date


class Scrobble(Config):

    artist = Field(six.text_type, required=True)
    track = Field(six.text_type, required=True)
    timestamp = Field(query_date, required=True)
    mbid = Field(six.text_type)
    album = Field(six.text_type)
    context = Field(six.text_type)
    streamId = Field(six.text_type, key='stream_id')
    chosenByUser = Field(int, key='chosen_by_user', default=1)
    trackNumber = Field(int, key='track_number')
    albumArtist = Field(six.text_type, key='album_artist')
    duration = Field(int)


class CorrectedTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


class TrackInfo(ApiConfig):

    __inherits__ = [_TrackBase]

    streamable = Field(bool_from_int, required=True)

    duration = Field(int, required=True)
    listeners = Field(int, required=True)
    playcount = Field(int, required=True)
    toptags = Field(lambda value: [Tag(tag) for tag in value['tag']],
                    required=True)
    wiki = Field(Wiki, required=True)

    album_name = Field(extract('title'), key='album', required=True)
    album_mbid = Field(extract('mbid', coerce=string_or_null), key='album',
                       required=True)
    album_url = Field(extract('url', coerce=string_or_null), key='album')
    album_images = Field(extract('image', coerce=images), default=[],
                         key='album')

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


class SearchTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    artist_name = Field(six.text_type, key='artist', required=True)
    listeners = Field(int, required=True)
    streamable = Field(bool_from_int, required=True)
