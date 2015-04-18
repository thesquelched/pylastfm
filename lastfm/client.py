from itertools import chain
import six

from lastfm.response.common import PaginateMixin
from lastfm import auth, constants
from lastfm.util import Signer, PaginatedIterator
from lastfm.api import user


import requests


AUTHENTICATED_METHODS = frozenset([
])


class ApiInfo(object):

    def __init__(self, key, secret, url=None, session_key=None):
        self._key = key
        self._secret = secret
        self._url = url or constants.DEFAULT_URL
        self._session_key = session_key

    @property
    def key(self):
        return self._key

    @property
    def secret(self):
        return self._secret

    @property
    def url(self):
        return self._url

    @property
    def session_key(self):
        return self._session_key

    @property
    def authenticated(self):
        return self.session_key is not None

    def add_session_key(self, session_key):
        """Return a copy of this object with the updated session key"""
        return ApiInfo(
            self.key,
            self.secret,
            url=self.url,
            session_key=session_key)


class LastFM(object):

    def __init__(self,
                 api_key,
                 api_secret,
                 username=None,
                 password=None,
                 url=None,
                 session_key=None):
        self._api_info = api_info = ApiInfo(
            api_key,
            api_secret,
            url=url or constants.DEFAULT_URL,
            session_key=session_key)

        self._signer = signer = Signer(self)
        self._auth = auth.Password(signer,
                                   api_info,
                                   username,
                                   password)

        self.user = user.User(self)

    @property
    def api_info(self):
        return self._api_info

    @api_info.setter
    def api_info(self, value):
        self._api_info = value

    def authenticate(self):
        """
        Authenticate with the LastFM API. Has side effects.

        :returns: The LastFM client object
        """

        session_key = self._auth.session_key()
        self.api_info = self.api_info.add_session_key(session_key)

        return self

    def _sign(self, params):
        """
        Sign the request parameters to send to the LastFM API
        """
        if not self.api_info.authenticated:
            self.authenticate()

        return self._signer(params)

    def _request(self, http_method, method, unwrap=None, params=None,
                 **kwargs):
        """
        Make a LastFM API request, returning the parsed JSON from the response.
        """
        if params is None:
            params = {}

        params.update(api_key=self.api_info.key,
                      method=method,
                      format='json')

        if method in AUTHENTICATED_METHODS:
            params = self._sign(params)

        resp = requests.request(http_method,
                                self.api_info.url,
                                params=params,
                                **kwargs)
        resp.raise_for_status()

        data = resp.json()
        return data[unwrap] if unwrap else data

    def _paginate_request(self, http_method, method, collection_key,
                          params=None, **kwargs):
        if params is None:
            params = {}
        params.update(limit=200)

        resp = self._request(http_method, method, params=params, **kwargs)
        if collection_key not in resp and resp.get('total') == '0':
            resp[collection_key] = []
            return resp

        attributes = PaginateMixin(resp).attributes

        pagerange = six.moves.range(2, attributes.total_pages + 1)

        def pagequery(page, http_method=http_method, method=method,
                      collection_key=collection_key, kwargs=kwargs):
            params = kwargs.copy()
            params['page'] = page

            data = self._request(http_method, method, params=params, **kwargs)
            return data[collection_key]

        thispage = resp[collection_key]
        remaining_pages = chain.from_iterable(pagequery(page)
                                              for page in pagerange)
        iterator = chain(thispage, remaining_pages)

        resp[collection_key] = PaginatedIterator(
            attributes.total_pages,
            attributes.total,
            iterator)

        return resp
