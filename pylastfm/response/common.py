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
        return bool(int(value))
    except (TypeError, ValueError):
        return False


def extract(first, *rest, **kwargs):
    """
    extract(*keys, coerce=None)

    Extracts a value from a series of nested dicts, and then optionally coerces
    the final result to the desired type
    """
    kw_coerce = kwargs.pop('coerce', None)
    required = kwargs.pop('required', False)

    if kwargs:
        key = list(kwargs.keys())[0]
        raise TypeError(
            "extract() got an unexpected keyword argument '{}'".format(key))

    def extractor(value, keys=(first,) + rest, coerce=kw_coerce,
                  required=required):
        result = value
        for key in keys:
            try:
                result = result[key]
            except KeyError:
                if required:
                    raise

                result = None
                break

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

    def __repr__(self):
        properties = set(
            key for key, value in six.iteritems(self.__class__.__dict__)
            if not key.startswith('_') and isinstance(value, property))

        # 'id' and 'name' always go at the front of the list
        ordered = []
        for key in ('name',):
            if key in properties:
                value = repr(getattr(self, key))
                ordered.append("{0}={1}".format(key, value))
                properties.remove(key)

        ordered.extend(sorted(properties))

        return '{0}({1})'.format(self.__class__.__name__, ', '.join(ordered))


class _TrackBase(Config):

    name = Field(six.text_type, required=True)
    url = Field(six.text_type, required=True)
    mbid = Field(six.text_type)
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
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


class Track(ApiConfig):

    __inherits__ = [_TrackBase]

    streamable = Field(extract('#text', coerce=bool_from_int), required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


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


class CorrectedTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


class TopTrack(ApiConfig):

    __inherits__ = [_TrackBase]

    rank = Field(extract('rank', coerce=int), key='@attr', required=True)
    streamable = Field(bool_from_int, required=True)
    listeners = Field(int, required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')


class Tag(ApiConfig):

    name = Field(six.text_type, required=True)
    url = Field(six.text_type)


class Wiki(ApiConfig):

    content = Field(six.text_type, required=True)
    summary = Field(six.text_type, required=True)
    published = Field(six.text_type, required=True)
    published = Field(dateparse, required=True)


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


class CorrectedArtist(ApiConfig):

    name = Field(extract('name'), key='artist', required=True)
    mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                 required=True)
    url = Field(extract('url', coerce=string_or_null), key='artist')


class _ArtistBase(Config):

    name = Field(six.text_type, required=True)
    mbid = Field(six.text_type)
    url = Field(six.text_type)
    streamable = Field(bool_from_int)
    images = Field(images, default=[], key='image')


class SimilarArtist(ApiConfig):

    __inherits__ = [_ArtistBase]


class Artist(ApiConfig):

    __inherits__ = [_ArtistBase]

    on_tour = Field(bool_from_int, required=True, key='ontour')
    listeners = Field(extract('listeners', coerce=int), key='stats',
                      required=True)
    playcount = Field(extract('playcount', coerce=int), key='stats',
                      required=True)
    bio = Field(six.text_type)
    tags = Field(lambda value: [Tag(tag) for tag in value['tag']],
                 required=True)
    similar = Field(
        lambda value: [SimilarArtist(item) for item in value['artist']],
        required=True)


class SearchArtist(ApiConfig):

    __inherits__ = [_ArtistBase]

    listeners = Field(int, required=True)


class LibraryArtist(ApiConfig):

    __inherits__ = [_ArtistBase]

    playcount = Field(int, required=True)
    tagcount = Field(int, required=True)


class Album(ApiConfig):

    name = Field(six.text_type, required=True)
    mbid = Field(six.text_type)
    url = Field(six.text_type, required=True)
    playcount = Field(int, required=True)

    artist_name = Field(extract('name'), key='artist', required=True)
    artist_mbid = Field(extract('mbid', coerce=string_or_null), key='artist',
                        required=True)
    artist_url = Field(extract('url', coerce=string_or_null), key='artist')
