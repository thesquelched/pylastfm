import six
import pytest

from pylastfm.response import chart
from pylastfm.util import PaginatedIterator


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_artists(client, limit_one):
    resp = client.chart.get_top_artists(limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    assert isinstance(six.next(resp), chart.Artist)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)


@pytest.mark.live
def test_get_top_tags(client):
    resp = client.chart.get_top_tags()
    assert isinstance(resp, PaginatedIterator)
    assert isinstance(six.next(resp), chart.Tag)


@pytest.mark.live
@pytest.mark.parametrize('limit_one', [False, True])
def test_get_top_tracks(client, limit_one):
    resp = client.chart.get_top_tracks(limit=1 if limit_one else None)
    assert isinstance(resp, PaginatedIterator)

    assert isinstance(six.next(resp), chart.Track)

    if limit_one:
        pytest.raises(StopIteration, six.next, resp)
