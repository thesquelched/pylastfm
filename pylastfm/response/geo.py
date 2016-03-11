from figgis import Field
from pylastfm.response.common import ApiConfig, TagTrack, _ArtistBase


class Track(ApiConfig):

    __inherits__ = [TagTrack]

    listeners = Field(int, required=True)


class Artist(ApiConfig):

    __inherits__ = [_ArtistBase]

    listeners = Field(int, required=True)
