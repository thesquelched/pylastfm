import six
from figgis import Config, Field
from dateutil.parser import parse as dateparse

from pylastfm.util import ceildiv


def integer(value):
    return int(value) if value else 0


def string_or_null(value):
    return six.text_type(value) if value else None


def bool_from_int(value):
    try:
        bool(int(value))
    except (TypeError, ValueError):
        return False


def extract(first, *rest, **kwargs):
    """
    extract(*keys, coerce=None)

    Extracts a value from a series of nested dicts, and then optionally coerces
    the final result to the desired type
    """
    if kwargs and 'coerce' not in kwargs:
        key = list(kwargs.keys())[0]
        raise TypeError(
            "extract() got an unexpected keyword argument '{}'".format(key))

    def extractor(value, keys=(first,) + rest, coerce=kwargs.get('coerce')):
        result = value
        for key in keys:
            result = result[key]

        return coerce(result) if coerce else result
    return extractor


def images(value):
    """Converts list of image dicts to a single dict of (size, url) pairs"""
    return dict((item['size'], item['#text']) for item in value)


class PaginatedAttributes(Config):

    page = Field(integer, required=True)
    total_pages = Field(integer, key='totalPages', required=True)
    total = Field(integer, required=True)


class PaginateMixin(Config):

    """
    Mixin that parses attributes required for pagination
    """

    attributes = Field(PaginatedAttributes, required=True, key='@attr')

    @property
    def page(self):
        return self.attributes.page

    @property
    def total_pages(self):
        return self.attributes.total_pages

    @property
    def total(self):
        return self.attributes.total


class SearchPaginateMixin(Config):

    items_per_page = Field(integer, required=True,
                           key='opensearch:itemsPerPage')
    start_index = Field(integer, required=True, key='opensearch:startIndex')
    total = Field(integer, required=True, key='opensearch:totalResults')

    @property
    def page(self):
        return self.start_index // self.items_per_page

    @property
    def total_pages(self):
        return ceildiv(self.total, self.items_per_page)


######################################################################
# Common response objects
######################################################################

class ApiConfig(Config):

    def __init__(self, properties, client=None):
        super(ApiConfig, self).__init__(properties)
        self._client = client


class _TrackBase(Config):

    name = Field(six.text_type, required=True)
    url = Field(six.text_type, required=True)
    mbid = Field(six.text_type, required=True)
    date = Field(extract('#text', coerce=dateparse))
    images = Field(images, default=[], key='image')


class ArtistTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    streamable = Field(bool_from_int, required=True)

    album_name = Field(extract('#text'), key='album', required=True)
    album_mbid = Field(extract('mbid', coerce=string_or_null), key='album',
                       required=True)

    artist_name = Field(extract('#text'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('mbid', coerce=string_or_null), key='artist')


class Track(ApiConfig):

    __inherits__ = [_TrackBase]

    streamable = Field(extract('#text', coerce=bool_from_int), required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('mbid', coerce=string_or_null), key='artist')


class RecentTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    streamable = Field(bool_from_int, required=True)

    album_name = Field(extract('#text'), key='album', required=True)
    album_mbid = Field(extract('mbid', coerce=string_or_null), key='album',
                       required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('mbid', coerce=string_or_null), key='artist')
    artist_images = Field(extract('image', coerce=images), default=[],
                          key='artist')

    loved = Field(bool_from_int, required=True)


class CorrectedTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('mbid', coerce=string_or_null), key='artist')


class Tag(Config):

    name = Field(six.text_type, required=True)
    url = Field(six.text_type)


class Wiki(Config):

    content = Field(six.text_type, required=True)
    summary = Field(six.text_type, required=True)
    published = Field(six.text_type, required=True)
    published = Field(dateparse, required=True)


class TrackInfo(ApiConfig):

    __inherits__ = [_TrackBase]

    streamable = Field(bool_from_int, required=True)

    duration = Field(int, required=True)
    id = Field(int, required=True)
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
    artist_url = Field(extract('mbid', coerce=string_or_null), key='artist')


class SearchTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    artist_name = Field(six.text_type, key='artist', required=True)
    listeners = Field(int, required=True)
    streamable = Field(bool_from_int, required=True)
