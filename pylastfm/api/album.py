from pylastfm.response import common
from pylastfm.response.album import AlbumInfo, Tag, TopTag, SearchAlbum
from pylastfm.api.api import API
from pylastfm.util import keywords


def _album_arguments(name, args):
    """Parse function arguments and return (artist, album, mbid).  Only use
    with function that take those arguments."""
    if len(args) == 1:
        mbid = args[0]
        artist, album = None, None
    elif len(args) == 2:
        artist, album = args
        mbid = None
    else:
        raise TypeError('{0}() takes either (artist, album) or '
                        '(mbid,)'.format(name))

    return artist, album, mbid


class Resource(API):

    def add_tags(self, artist, album, *tags):
        """
        Tag an album using a list of user supplied tags.

        http://www.last.fm/api/show/album.addTags
        """
        self._request(
            'POST',
            'album.addTags',
            data=dict(
                artist=artist,
                album=album,
                tags=','.join(str(tag) for tag in tags),
            ),
        )

    @keywords('username', 'language', autocorrect=False)
    def get_info(self, *args, **kwargs):
        """
        Get the metadata and tracklist for an album on Last.fm using the album
        name or a musicbrainz id.

        http://www.last.fm/api/show/album.getInfo
        """
        artist, album, mbid = _album_arguments('get_info', args)

        resp = self._request(
            'GET',
            'album.getInfo',
            params=dict(
                artist=artist,
                album=album,
                mbid=mbid,
                user=kwargs.get('username') or self._client.username,
                autocorrect=int(kwargs['autocorrect']),
                lang=kwargs.get('language'),
            ),
            unwrap='album',
        )

        return self.model(AlbumInfo, resp)

    @keywords('username', autocorrect=False)
    def get_tags(self, *args, **kwargs):
        """
        Get the tags applied by an individual user to an album on Last.fm. To
        retrieve the list of top tags applied to an album by all users use
        album.getTopTags.

        http://www.last.fm/api/show/album.getTags
        """
        artist, album, mbid = _album_arguments('get_tags', args)

        resp = self._request(
            'GET',
            'album.getTags',
            params=dict(
                artist=artist,
                album=album,
                mbid=mbid,
                user=kwargs.get('username') or self._client.username,
                autocorrect=int(kwargs['autocorrect']),
            ),
            unwrap='tags',
        ).get('tag') or []

        return [self.model(Tag, item) for item in resp]

    @keywords(autocorrect=False)
    def get_top_tags(self, *args, **kwargs):
        """
        Get the top tags for an album on Last.fm, ordered by popularity.

        http://www.last.fm/api/show/album.getTopTags
        """
        artist, album, mbid = _album_arguments('get_top_tags', args)

        resp = self._request(
            'GET',
            'album.getTopTags',
            params=dict(
                artist=artist,
                album=album,
                mbid=mbid,
                autocorrect=int(kwargs['autocorrect']),
            ),
            unwrap='toptags',
        )['tag']

        return [self.model(TopTag, item) for item in resp]

    def remove_tag(self, artist, album, tag):
        """
        Remove a user's tag from an album.

        http://www.last.fm/api/show/album.removeTag
        """
        self._request(
            'POST',
            'album.removeTag',
            data=dict(
                artist=artist,
                album=album,
                tag=tag,
            ),
        )

    def search(self, album, limit=None):
        """
        Search for an album by name. Returns album matches sorted by
        relevance.

        http://www.last.fm/api/show/album.search
        """
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'album.search',
            'albummatches.album',
            data=dict(
                album=album,
            ),
            unwrap='results',
            perpage=perpage,
            limit=limit,
            paginate_attr_class=common.SearchPaginateMixin,
        )['albummatches']['album']

        return self.model_iterator(SearchAlbum, resp)
