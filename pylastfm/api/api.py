from pylastfm.response.common import ApiConfig


class API(object):
    """Base class for LastFM API endpoints"""

    def __init__(self, client):
        self._client = client

    def _request(self, *args, **kwargs):
        return self._client._request(*args, **kwargs)

    def _paginate_request(self, *args, **kwargs):
        return self._client._paginate_request(*args, **kwargs)

    def model_iterator(self, model_class, iterator):
        """
        Create a new iterator from an existing PaginatedIterator by applying
        the model class to each item
        """
        return iterator.map(lambda item: self.model(model_class, item))

    def model(self, model_class, data):
        """
        Return an instance of the model created form the data
        """
        if issubclass(model_class, ApiConfig):
            kwargs = {'client': self._client}
        else:
            kwargs = {}

        return model_class(data, **kwargs)
