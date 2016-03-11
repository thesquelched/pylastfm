from pylastfm.response import common
from pylastfm.api.api import API
from iso3166 import countries


class Geo(API):

    def get_top_artists(self, country, limit=None):
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'POST',
            'geo.getTopArtists',
            'artist',
            params=dict(
                country=countries.get(country).name,
            ),
            perpage=perpage,
            limit=limit,
            unwrap='topartists',
        )['artist']

        return self.model_iterator(common.GeoArtist, resp)

    def get_top_tracks(self, country, limit=None):
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'POST',
            'geo.getTopTracks',
            'track',
            params=dict(
                country=countries.get(country).name,
            ),
            perpage=perpage,
            limit=limit,
            unwrap='tracks',
        )['track']

        return self.model_iterator(common.GeoTrack, resp)