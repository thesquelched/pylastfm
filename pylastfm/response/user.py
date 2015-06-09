from pylastfm.response.common import PaginateMixin, Track
from figgis import Config, Field, ListField


class LovedTracks(Config):

    __inherits__ = [PaginateMixin]

    track = ListField(Track, required=True)


######################################################################
# API Responses
######################################################################

class GetLovedTracks(Config):

    lovedtracks = Field(LovedTracks, required=True)
