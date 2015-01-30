from lastfm.response.common import PaginateMixin
from lastfm import util
from figgis import Config, Field, ListField


class Artist(Config):

    mbid = Field()
    name = Field(required=True)
    url = Field()


class Track(Config):

    name = Field(required=True)
    url = Field()
    mbid = Field()

    date = Field(util.parse_date)
    image = ListField(util.parse_image, default=[])
    artist = Field(Artist)
    streamable = Field(util.parse_bool_from_int)


class LovedTracks(Config):

    __inherits__ = [PaginateMixin]

    track = ListField(Track, required=True)


######################################################################
# API Responses
######################################################################

class GetLovedTracks(Config):

    lovedtracks = Field(LovedTracks, required=True)
