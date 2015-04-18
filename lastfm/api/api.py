class API(object):
    """Base class for LastFM API endpoints"""

    def __init__(self, client):
        self._client = client
