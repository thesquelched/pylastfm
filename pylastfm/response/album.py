import six
from figgis import Field
from pylastfm.response.common import (ApiConfig, _AlbumBase, dateparse,
                                      _TrackBase, bool_from_int, extract,
                                      string_or_null, images, _TagBase)


class Track(ApiConfig):

    __inherits__ = [_TrackBase]

    track = Field(extract('rank', coerce=int), key='@attr')
    streamable = Field(extract('#text', coerce=bool_from_int), required=True)
    duration = Field(int, required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


class AlbumInfo(ApiConfig):

    __inherits__ = [_AlbumBase]

    images = Field(images, default=[], key='image')
    artist_name = Field(six.text_type, key='artist', required=True)

    wiki_content = Field(extract('content'), key='wiki', required=True)
    wiki_summary = Field(extract('summary'), key='wiki', required=True)
    wiki_published = Field(extract('published', coerce=dateparse),
                           key='wiki', required=True)

    tracks = Field(lambda value: [Track(item) for item in value['track']])


class Tag(ApiConfig):

    __inherits__ = [_TagBase]

    url = Field(six.text_type)


class TopTag(ApiConfig):

    __inherits__ = [Tag]

    count = Field(int, required=True)


class SearchAlbum(ApiConfig):

    __inherits__ = [_AlbumBase]

    artist_name = Field(six.text_type, key='artist', required=True)
    streamable = Field(bool_from_int, required=True)
    images = Field(images, default=[], key='image')
