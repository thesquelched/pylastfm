from pylastfm.response import common
from pylastfm.api.api import API


class Library(API):

    def get_artists(self, username=None, limit=None):
        """
        A paginated list of all the artists in a user's library, with play
        counts and tag counts.

        http://www.last.fm/api/show/library.getArtists
        """
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'library.getArtists',
            'artist',
            params=dict(
                user=username or self._client.username,
            ),
            unwrap='artists',
            perpage=perpage,
            limit=limit,
        )['artist']

        return self.model_iterator(common.LibraryArtist, resp)
