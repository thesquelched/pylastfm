[![Build Status](https://travis-ci.org/thesquelched/pylastfm.svg?branch=master)](https://travis-ci.org/thesquelched/pylastfm)

pylastfm
========

Lazy LastFM API bindings in python


Pagination
==========

Paginated API methods (i.e. methods that accept `page` and `limit` parameters) automatically query all results, returning a `PaginatedIterator`.  This works like a standard iterator, except that it provides the `pages` attribute, which is the same as the total number of API requests it will take to exhaus all results.  It also provides the `map` method, which works the same as the `map` function, except that it produces another `PaginatedIterator`.


Examples
========

```python
>>> from lastfm import LastFM

>>> # Current, only password authentication is supported
>>> client = LastFM('api_key', 'api_secret', username='username', password='password')

>>> tracks = client.user.get_loved_tracks('some_user')
>>> tracks
<PaginatedIterator(5 pages)>

>>> track = next(tracks)
>>> track
<lastfm.response.common.Track at 0x102458a50>

>>> '{0} - {1}'.format(track.artist_name, track.name)
'Low - On My Own'

>>> track.to_dict()
{'artist_mbid': u'0c39e6da-14c7-4d7e-954f-a3fbd6ab7225',
 'artist_name': u'Low',
 'artist_url': u'0c39e6da-14c7-4d7e-954f-a3fbd6ab7225',
 'date': datetime.datetime(2015, 4, 17, 18, 54),
 'images': {u'extralarge': u'http://userserve-ak.last.fm/serve/300x300/97233023.png',
  u'large': u'http://userserve-ak.last.fm/serve/126/97233023.png',
  u'medium': u'http://userserve-ak.last.fm/serve/64s/97233023.png',
  u'small': u'http://userserve-ak.last.fm/serve/34s/97233023.png'},
 'mbid': u'9afc711b-42cd-4ddc-9a29-f9a39cf47891',
 'name': u'On My Own',
 'streamable': None,
 'url': u'http://www.last.fm/music/Low/_/On+My+Own'}

>>> other_tracks = list(tracks)
>>> len(other_tracks)
1000

>>> client.track.unlove(track.artist_name, track.name)
```
