import six
import pytest

from pylastfm.response import album
from pylastfm.util import PaginatedIterator


@pytest.mark.live
@pytest.mark.parametrize('autocorrect,args', [
    (False, ('Pink Floyd', 'The Wall')),
    (False, ('d4611812-e7cd-42bf-885a-b1cea9fd52bc',)),
    (True, ('Pink Floyd', 'The Wall')),
    (True, ('d4611812-e7cd-42bf-885a-b1cea9fd52bc',)),
])
def test_get_info(client, autocorrect, args):
    kwargs = {'autocorrect': autocorrect}
    resp = client.album.get_info(*args, **kwargs)
    assert isinstance(resp, album.AlbumInfo)


@pytest.mark.live
@pytest.mark.parametrize('autocorrect', [False, True])
def test_get_tags(client, autocorrect):
    resp = client.album.get_tags('Pink Floyd', 'The Wall',
                                 autocorrect=autocorrect)
    assert isinstance(resp, list)
    assert all(isinstance(item, album.Tag) for item in resp)


@pytest.mark.live
@pytest.mark.parametrize('autocorrect', [False, True])
def test_get_top_tags(client, autocorrect):
    resp = client.album.get_top_tags('Pink Floyd', 'The Wall',
                                     autocorrect=autocorrect)
    assert isinstance(resp, list)
    assert all(isinstance(item, album.TopTag) for item in resp)


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_search(client, limit_one):
    resp = client.album.search('The Wall', limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    assert isinstance(six.next(resp), album.SearchAlbum)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)
