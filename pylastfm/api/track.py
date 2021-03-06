import six
import itertools
from types import GeneratorType

from pylastfm.response import common, track as response
from pylastfm.api.api import API
from pylastfm.util import keywords


def _track_arguments(name, args):
    """Parse function arguments and return (artist, track, mbid).  Only use
    with function that take those arguments."""
    if len(args) == 1:
        mbid = args[0]
        artist, track = None, None
    elif len(args) == 2:
        artist, track = args
        mbid = None
    else:
        raise TypeError('{0}() takes either (artist, track) or '
                        '(mbid,)'.format(name))

    return artist, track, mbid


class Resource(API):

    def add_tags(self, artist, track, tags):
        """
        Tag an album using a list of user supplied tags. Only accepts up to 10
        tags.

        http://www.last.fm/api/show/track.addTags
        """
        # TODO: Can you add more than 10 tags?
        self._request(
            'POST',
            'track.addTags',
            data=dict(
                artist=artist,
                track=track,
                tags=','.join(tags[:10]),
            )
        )

    def get_correction(self, artist, track):
        """
        Use the last.fm corrections data to check whether the supplied track
        has a correction to a canonical track

        http://www.last.fm/api/show/track.getCorrection
        """
        resp = self._request(
            'GET',
            'track.getCorrection',
            params=dict(
                artist=artist,
                track=track,
            ),
            unwrap='corrections',
        )
        return self.model(response.CorrectedTrack, resp['correction']['track'])

    @keywords('username', autocorrect=False)
    def get_info(self, *args, **kwargs):
        """
        get_info(*args, username=None, autocorrect=False)

        Get the metadata for a track on Last.fm using the artist/track name or
        a musicbrainz id.

        http://www.last.fm/api/show/track.getInfo
        """
        artist, track, mbid = _track_arguments('get_info', args)

        resp = self._request(
            'GET',
            'track.getInfo',
            params=dict(
                artist=artist,
                track=track,
                mbid=mbid,
                username=kwargs.get('username', self._client.username),
                autocorrect=int(kwargs['autocorrect']),
            ),
            unwrap='track',
        )
        return self.model(response.TrackInfo, resp)

    @keywords(autocorrect=False, limit=None)
    def get_similar(self, *args, **kwargs):
        """
        get_similar(*args, autocorrect=False, limit=None)

        Get the similar tracks for this track on Last.fm, based on listening
        data. May be invoked in two ways:

            get_similar('mbid')
            get_similar('artist', 'track')

        http://www.last.fm/api/show/track.getSimilar
        """
        artist, track, mbid = _track_arguments('get_similar', args)

        limit = kwargs.get('limit')

        resp = self._request(
            'GET',
            'track.getSimilar',
            unwrap='similartracks',
            collection_key='track',
            params=dict(
                artist=artist,
                track=track,
                mbid=mbid,
                autocorrect=int(kwargs['autocorrect']),
                limit=int(limit) if limit is not None else limit,
            )
        )
        return [self.model(common.Track, item) for item in resp]

    @keywords('username', autocorrect=False)
    def get_tags(self, *args, **kwargs):
        """
        get_tags(*args, username=None, autocorrect=False)

        Get the tags applied by an individual user to a track on Last.fm. To
        retrieve the list of top tags applied to a track by all users use
        track.getTopTags. Can be invoked in two ways:

            get_tags('mbid')
            get_tags('artist', 'track')

        http://www.last.fm/api/show/track.getTags
        """
        artist, track, mbid = _track_arguments('get_tags', args)

        resp = self._request(
            'GET',
            'track.getTags',
            unwrap='tags',
            params=dict(
                artist=artist,
                track=track,
                mbid=mbid,
                autocorrect=int(kwargs['autocorrect']),
                user=kwargs.get('username', self._client.username),
            )
        )['tag']

        return [self.model(common.Tag, tag) for tag in resp]

    @keywords(autocorrect=False)
    def get_top_tags(self, *args, **kwargs):
        """
        get_top_tags(*args, autocorrect=False)

        Get the top tags for this track on Last.fm, ordered by tag count.
        Supply either track & artist name or mbid. Can be invoked in
        two ways:

            get_top_tags('mbid')
            get_top_tags('artist', 'track')

        http://www.last.fm/api/show/track.getTopTags
        """
        artist, track, mbid = _track_arguments('get_top_tags', args)

        resp = self._request(
            'GET',
            'track.getTopTags',
            unwrap='toptags',
            params=dict(
                artist=artist,
                track=track,
                mbid=mbid,
                autocorrect=int(kwargs['autocorrect']),
            )
        )
        return [self.model(common.Tag, tag) for tag in resp['tag']]

    def love(self, artist, track):
        """
        Love a track for a user profile.

        http://www.last.fm/api/show/track.love
        """
        self._request(
            'POST',
            'track.love',
            data=dict(
                artist=artist,
                track=track,
            )
        )

    def remove_tag(self, artist, track, tag):
        """
        Remove a user's tag from a track.

        http://www.last.fm/api/show/track.removeTag
        """
        self._request(
            'POST',
            'track.remove_tag',
            data=dict(
                artist=artist,
                track=track,
                tag=tag,
            )
        )

    def _marshal_scrobbles(self, scrobbles):
        """Marshal each scrobble in the correct format for the API"""
        data = (response.Scrobble(scrobble).to_dict()
                for scrobble in scrobbles)
        return dict(itertools.chain.from_iterable(
            [('{0}[{1}]'.format(key, i), value)
             for key, value in scrobble.items()]
            for i, scrobble in enumerate(data)
        ))

    def scrobble(self, *args, **kwargs):
        """
        Scrobble one or more tracks. Each scrobble must be a dictionary with
        the following required values:

            artist: The artist name.
            track: The track name.
            timestamp: The time the track started playing; can be a datetime
                       object or any parsable date string

        Each scrobble may also have the following optional values:

            mbid: The MusicBrainz Track ID.
            album: The album name.
            context: Sub-client version (not public, only enabled for
                     certain API keys)
            stream_id: The stream id for this track received from the
                       radio.getPlaylist service, if scrobbling Last.fm radio
            chosen_by_user: `True` if the user chose this song, or `False` if
                            the song was chosen by someone else (such as a
                            radio station or recommendation service).
            track_number: The track number of the track on the album.
            album_artist: The album artist - if this differs from the track
                          artist.
            duration: The length of the track in seconds.

        You may call this function in one of two ways:

            scrobble([scrobble1, scrobble2, ...])
            scrobble(artist=artist, track=track, timestamp=timestamp, ...)

        In the first case, you may call the function with a tuple, list, or
        generator.

        http://www.last.fm/api/show/track.scrobble
        """
        if args and isinstance(args[0], (tuple, list, GeneratorType)):
            if kwargs:
                raise TypeError("scrobbles() got unexpected keyword "
                                "argument: '{1}'".format(
                                    six.next(iter(kwargs))))

            data = dict(self._marshal_scrobbles(args[0]))
        elif kwargs:
            data = dict(self._marshal_scrobbles([kwargs]))
        else:
            raise TypeError('scrobbles() expected an iterable or keyword '
                            'arguments, but not both')

        self._request(
            'POST',
            'track.scrobble',
            data=data,
        )

    def search(self, track, artist=None, limit=None):
        """
        Search for a track by track name. Returns track matches sorted by
        relevance.

        http://www.last.fm/api/show/track.search
        """
        # limited by LastFM API
        perpage = min(30, limit) if limit else 30

        resp = self._paginate_request(
            'GET',
            'track.search',
            'trackmatches.track',
            unwrap='results',
            paginate_attr_class=common.SearchPaginateMixin,
            limit=limit,
            perpage=perpage,
            params=dict(
                artist=artist,
                track=track,
            )
        )['trackmatches']['track']

        return self.model_iterator(response.SearchTrack, resp)

    def unlove(self, artist, track):
        """
        UnLove a track for a user profile.

        http://www.last.fm/api/show/track.unlove
        """
        self._request(
            'POST',
            'track.unlove',
            data=dict(
                artist=artist,
                track=track,
            )
        )

    @keywords('album', 'track_number', 'context', 'duration', 'album_artist')
    def update_now_playing(self, *args, **kwargs):
        """
        http://www.last.fm/api/show/track.updateNowPlaying
        """
        artist, track, mbid = _track_arguments('get_info', args)

        self._request(
            'POST',
            'track.updateNowPlaying',
            data=dict(
                artist=artist,
                track=track,
                mbid=mbid,
                album=kwargs.get('album'),
                trackNumber=kwargs.get('track_number'),
                context=kwargs.get('context'),
                duration=kwargs.get('duration'),
                albumArtist=kwargs.get('album_artist'),
            )
        )
