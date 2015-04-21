from itertools import chain
import six
import requests
from requests.adapters import HTTPAdapter

from lastfm.response.common import PaginateMixin
from lastfm import auth, constants, error
from lastfm.util import Signer, PaginatedIterator
from lastfm.api import user


def prefixed(prfx, *methods):
    """Return reach method prefixed by the given prefix"""
    return ['{0}.{1}'.format(prfx, method) for method in methods]


AUTHENTICATED_METHODS = frozenset(
    prefixed('user',
             'getRecentStations',
             'getRecommendedArtists',
             'getRecommendedEvents',
             'shout')
)


ERROR = 'error'
MESSAGE = 'message'


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

        # Fix SSL issues for LastFM API
        self._session = requests.Session()
        self._session.mount(constants.DEFAULT_URL, HTTPAdapter(max_retries=2))

        # Exposed API objects
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

        return self._signer(**params)

    def _request_args(self, http_method, method, kwargs):
        if http_method in ('PUT', 'POST'):
            data_key = 'data'
        else:
            data_key = 'params'

        data = kwargs.get(data_key)
        if data is None:
            data = {}

        data.update(api_key=self.api_info.key,
                    method=method,
                    format='json')

        if method in AUTHENTICATED_METHODS:
            data = self._sign(data)

        kwargs[data_key] = data
        return kwargs

    def _request(self, http_method, method, unwrap=None, **kwargs):
        """
        Make a LastFM API request, returning the parsed JSON from the response.
        """
        http_method = http_method.upper()
        request_args = self._request_args(http_method, method, kwargs)

        try:
            resp = self._session.request(http_method,
                                         self.api_info.url,
                                         **request_args)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            six.raise_from(
                error.ApiError(exc.response.status_code, exc.response.reason),
                exc)
        except requests.exceptions.RequestException as exc:
            newexc = error.LastfmError('Request error: {0}'.format(exc))
            six.raise_from(newexc, exc)

        result = resp.json()
        if ERROR in result:
            raise error.APIError(result[ERROR], result[MESSAGE])

        return result[unwrap] if unwrap else result

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
