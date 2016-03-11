from pylastfm.api.api import API
from pylastfm.response import chart


class Resource(API):

    def get_top_artists(self, limit=None):
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'chart.getTopArtists',
            'artist',
            perpage=perpage,
            limit=limit,
            unwrap='artists'
        )['artist']

        return self.model_iterator(chart.Artist, resp)

    def get_top_tags(self):
        resp = self._paginate_request(
            'GET',
            'chart.getTopTags',
            'tag',
            unwrap='tags'
        )['tag']

        return self.model_iterator(chart.Tag, resp)

    def get_top_tracks(self, limit=None):
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'chart.getTopTracks',
            'track',
            perpage=perpage,
            limit=limit,
            unwrap='tracks'
        )['track']

        return self.model_iterator(chart.Track, resp)
