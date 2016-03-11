import six
from figgis import Field
from pylastfm.response.common import (_ArtistBase, ApiConfig, Tag as CTag,
                                      _TrackBase, extract, bool_from_int,
                                      string_or_null)


class Artist(ApiConfig):

    __inherits__ = [_ArtistBase]

    playcount = Field(int, required=True)
    listeners = Field(int, required=True)


class Tag(ApiConfig):

    __inherits__ = [CTag]

    url = Field(six.text_type, required=True)
    reach = Field(int, required=True)
    taggings = Field(int, required=True)


class Track(ApiConfig):

    __inherits__ = [_TrackBase]

    playcount = Field(int, required=True)
    listeners = Field(int, required=True)
    streamable = Field(bool_from_int, required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')
