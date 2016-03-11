from figgis import Field
from pylastfm.response.common import (ApiConfig, extract, string_or_null,
                                      _ArtistBase, _TrackBase, bool_from_int)


class CorrectedArtist(ApiConfig):

    name = Field(extract('name'), key='artist', required=True)
    mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                 required=True)
    url = Field(extract('url', coerce=string_or_null), key='artist')


class Track(ApiConfig):

    __inherits__ = [_TrackBase]

    rank = Field(extract('rank', coerce=int), key='@attr')
    streamable = Field(bool_from_int, required=True)
    listeners = Field(int, required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


class Artist(ApiConfig):

    __inherits__ = [_ArtistBase]

    listeners = Field(int, required=True)
