class API(object):
    """Base class for LastFM API endpoints"""

    def __init__(self, client):
        self._client = client

    def model_iterator(self, model_class, iterator):
        """
        Create a new iterator from an existing PaginatedIterator by applying
        the model class to each item
        """
        return iterator.map(
            lambda item: model_class(item, client=self._client))
