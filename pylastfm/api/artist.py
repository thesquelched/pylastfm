import six

from pylastfm.response import common
from pylastfm.api.api import API


class Artist(API):

    def add_tags(self, artist, *tags):
        """
        Tag an artist with one or more user supplied tags.

        http://www.last.fm/api/show/artist.addTags
        """
        return self._request(
            'POST',
            'artist.addTags',
            data=dict(
                artist=artist,
                tags=','.join(tags),
            )
        )

    def get_correction(self, artist):
        """
        Use the last.fm corrections data to check whether the supplied artist
        has a correction to a canonical artist.

        http://www.last.fm/api/show/artist.getCorrection
        """
        resp = self._request(
            'GET',
            'artist.getCorrection',
            params=dict(
                artist=artist,
            ),
            unwrap='corrections',
        )

        try:
            items = resp['correction']
            corrections = items if isinstance(items, list) else [items]
        except TypeError:
            # Sometimes, API returns a whitespace string instead of a dict.
            # Go figure
            if not isinstance(resp, six.text_type):
                raise

            corrections = []

        return [self.model(common.CorrectedArtist, correction)
                for correction in corrections]

    def get_info(self, artist=None, mbid=None, lang=None, autocorrect=False,
                 username=None):
        """
        Get the metadata for an artist. Includes biography, truncated at 300
        characters.  May be invoked in several ways:

            get_info('artist')
            get_info(mbid='mbid')

        http://www.last.fm/api/show/artist.getInfo
        """
        resp = self._request(
            'GET',
            'artist.getInfo',
            params=dict(
                artist=artist,
                mbid=mbid,
                lang=lang,
                autocorrect=int(autocorrect),
                username=username or self._client.username,
            ),
            unwrap='artist',
        )

        return self.model(common.Artist, resp)

    def get_similar(self, artist=None, mbid=None, autocorrect=False,
                    username=None):
        """
        Get all the artists similar to this artist.

        http://www.last.fm/api/show/artist.getSimilar
        """
        resp = self._request(
            'GET',
            'artist.getSimilar',
            params=dict(
                artist=artist,
                mbid=mbid,
                autocorrect=int(autocorrect),
                username=username or self._client.username,
            ),
            unwrap='similarartists'
        )

        return [self.model(common.SimilarArtist, similar)
                for similar in resp['artist']]

    def get_tags(self, artist=None, mbid=None, autocorrect=False,
                 username=None):
        """
        Get the tags applied by an individual user to an artist on Last.fm.
        If accessed as an authenticated service and you don't supply a user
        parameter then this service will return tags for the authenticated
        user. To retrieve the list of top tags applied to an artist by all
        users use `get_top_tags`.

        http://www.last.fm/api/show/artist.getTags
        """
        resp = self._request(
            'GET',
            'artist.getTags',
            params=dict(
                artist=artist,
                mbid=mbid,
                autocorrect=int(autocorrect),
                username=username or self._client.username,
            ),
            unwrap='tags'
        )

        tags = resp.get('tag', [])
        return [self.model(common.Tag, tag) for tag in tags]

    def get_top_albums(self, artist=None, mbid=None, autocorrect=False,
                       limit=None):
        """
        Get the top albums for an artist on Last.fm, ordered by popularity.

        http://www.last.fm/api/show/artist.getTopAlbums
        """
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'artist.getTopAlbums',
            'album',
            params=dict(
                artist=artist,
                mbid=mbid,
                autocorrect=int(autocorrect),
            ),
            limit=limit,
            perpage=perpage,
            unwrap='topalbums'
        )['album']

        return self.model_iterator(common.Album, resp)

    def get_top_tags(self, artist=None, mbid=None, autocorrect=False):
        """
        Get the top tags for an artist on Last.fm, ordered by popularity.

        http://www.last.fm/api/show/artist.getTopTags
        """
        resp = self._request(
            'GET',
            'artist.getTopTags',
            params=dict(
                artist=artist,
                mbid=mbid,
                autocorrect=int(autocorrect),
            ),
            unwrap='toptags'
        )['tag']

        return [self.model(common.Tag, tag) for tag in resp]

    def get_top_tracks(self, artist=None, mbid=None, autocorrect=False,
                       limit=None):
        """
        Get the top tracks by an artist on Last.fm, ordered by popularity.

        http://www.last.fm/api/show/artist.getTopTracks
        """
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'artist.getTopTracks',
            'track',
            params=dict(
                artist=artist,
                mbid=mbid,
                autocorrect=int(autocorrect),
            ),
            unwrap='toptracks',
            limit=limit,
            perpage=perpage,
        )['track']

        return self.model_iterator(common.TopTrack, resp)

    def remove_tag(self, artist, tag):
        """
        Remove a user's tag from an artist.

        http://www.last.fm/api/show/artist.removeTag
        """
        self._request(
            'POST',
            'artist.removeTag',
            data=dict(
                artist=artist,
                tag=tag,
            )
        )

    def search(self, artist, limit=None):
        """
        Search for an artist by name. Returns artist matches sorted by
        relevance.

        http://www.last.fm/api/show/artist.search
        """
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'artist.search',
            'artistmatches.artist',
            params=dict(artist=artist),
            unwrap='results',
            paginate_attr_class=common.SearchPaginateMixin,
            limit=limit,
            perpage=perpage,
        )['artistmatches']['artist']

        return self.model_iterator(common.SearchArtist, resp)
