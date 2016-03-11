from pylastfm.response import common
from pylastfm.api.api import API


class Tag(API):

    def get_top_albums(self, tag, limit=None):
        """
        Get the top albums tagged by this tag, ordered by tag count.

        http://www.last.fm/api/show/tag.getTopAlbums
        """
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'tag.getTopAlbums',
            'album',
            params=dict(
                tag=tag,
            ),
            unwrap='albums',
            limit=limit,
            perpage=perpage,
        )['album']

        return self.model_iterator(common.TagAlbum, resp)

    def get_top_artists(self, tag, limit=None):
        """
        Get the top artists tagged by this tag, ordered by tag count.

        http://www.last.fm/api/show/tag.getTopArtists
        """
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'tag.getTopArtists',
            'artist',
            params=dict(
                tag=tag,
            ),
            unwrap='topartists',
            limit=limit,
            perpage=perpage,
        )['artist']

        return self.model_iterator(common.TagArtist, resp)

    def get_top_tags(self):
        """
        """
        resp = self._request(
            'GET',
            'tag.getTopTags',
            unwrap='toptags',
        )['tag']

        ranked = (dict(list(item.items()) + [('rank', i)])
                  for i, item in enumerate(resp, start=1))
        return [self.model(common.TopTag, item) for item in ranked]

    def get_top_tracks(self, tag, limit=None):
        """
        """
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'tag.getTopTracks',
            'track',
            params=dict(
                tag=tag,
            ),
            unwrap='tracks',
            limit=limit,
            perpage=perpage,
        )['track']

        return self.model_iterator(common.TagTrack, resp)
