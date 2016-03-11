from figgis import Field
from pylastfm.response.common import ApiConfig, _ArtistBase


class Artist(ApiConfig):

    __inherits__ = [_ArtistBase]

    playcount = Field(int, required=True)
    tagcount = Field(int, required=True)
