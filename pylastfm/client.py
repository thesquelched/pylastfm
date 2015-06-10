import os
import six
import requests
from itertools import chain
from requests.adapters import HTTPAdapter
from six.moves.configparser import SafeConfigParser, NoOptionError

from pylastfm.response.common import PaginateMixin
from pylastfm import auth, constants, error
from pylastfm.util import (Signer, PaginatedIterator, nested_get, nested_in,
                           nested_set, ceildiv)
from pylastfm.api import user, track, auth as apiauth


def prefixed(prfx, *methods):
    """Return reach method prefixed by the given prefix"""
    return ['{0}.{1}'.format(prfx, method) for method in methods]


NOT_SPECIFIED = object()


AUTHENTICATED_METHODS = frozenset(chain(
    prefixed('user',
             'getRecentStations',
             'getRecommendedArtists',
             'getRecommendedEvents',
             'shout'),
    prefixed('track',
             'addTags',
             'ban',
             'love',
             'removeTag',
             'scrobble',
             'share',
             'unban',
             'unlove',
             'updateNowPlaying'),
))


ERROR = 'error'
MESSAGE = 'message'

MAX_LIMIT = 200
DEFAULT_LIMIT = MAX_LIMIT
DEFAULT_PERPAGE = 200


def _list_response(data):
    """
    If `data` is not a `list`, return a list with `data` as the only element.
    Otherwise, return `data`
    """
    if not isinstance(data, list):
        return [data]

    return data


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
                 session_key=None,
                 auth_method=None):
        """
        Create a LastFM client

        :param api_key: LastFM API key
        :param api_secret: LastFM API secret
        :param username: LastFM username
        :param password: LastFM account password, either in plaintext
            (password authentication) or hashed (hashed_password
            authentication)
        :param url: URL for the LastFM API
        :param session_key: Plaintext session key or path to session key file
            (only relevant for 'session_key' or 'session_key_file'
            authentication)
        :param auth_method: Authentication method; can be 'password',
            'hashed_password', 'session_key', or 'session_key_file'. If not
            specified, the client will attempt to determine the correct method
            from the parameters given.
        """
        self._username = username
        self._api_info = api_info = ApiInfo(
            api_key,
            api_secret,
            url=url or constants.DEFAULT_URL)

        self._signer = signer = Signer(self)

        if auth_method:
            auth_class = auth.AUTH_METHODS[auth_method]
        else:
            auth_class = self._get_auth_class(session_key)

        self._auth = auth_class(signer, api_info, username=username,
                                password=password, session_key=session_key)

        # Fix SSL issues for LastFM API
        self._session = requests.Session()
        self._session.mount(constants.DEFAULT_URL, HTTPAdapter(max_retries=2))

        # Exposed API objects
        self.user = user.User(self)
        self.track = track.Track(self)
        self.auth = apiauth.Auth(self)

    def _get_auth_class(self, session_key):
        if not session_key:
            return auth.AUTH_METHODS['password']

        if os.path.isfile(session_key):
            return auth.AUTH_METHODS['session_key_file']
        else:
            return auth.AUTH_METHODS['session_key']

    @classmethod
    def _getoption(cls, config, params, key, default=NOT_SPECIFIED):
        if key in params:
            value = params[key]
        else:
            try:
                value = config.get('lastfm', key)
            except NoOptionError:
                if default is NOT_SPECIFIED:
                    raise

                return default

        return value.strip()

    @classmethod
    def from_config(cls, path, **kwargs):
        """
        Create a LastFM instance from a config file in the following format:

            [lastfm]
            api_key = myapikey
            api_secret = myapisecret
            username = thesquelched
            password = plaintext_password

            # Can be 'password' or 'hashed_password'
            auth_method = password

        You can also override config values with keyword arguments.
        """
        config = SafeConfigParser()
        config.add_section('lastfm')
        config.read(os.path.expanduser(os.path.expandvars(path)))

        return LastFM(
            cls._getoption(config, kwargs, 'api_key'),
            cls._getoption(config, kwargs, 'api_secret'),
            username=cls._getoption(config, kwargs, 'username', None),
            password=cls._getoption(config, kwargs, 'password', None),
            auth_method=cls._getoption(config, kwargs, 'auth_method', None),
            session_key=cls._getoption(config, kwargs, 'session_key', None),
            url=cls._getoption(config, kwargs, 'url', None),
        )

    @property
    def username(self):
        return self._username

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

    def _request(self, http_method, method, unwrap=None, collection_key=None,
                 **kwargs):
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

        unwrapped = result[unwrap] if unwrap else result
        if collection_key is None:
            return unwrapped

        coll_keys = collection_key.split('.')
        return _list_response(nested_get(unwrapped, coll_keys))

    def _paginate_request(self, http_method, method, collection_key,
                          perpage=None, limit=None, params=None,
                          paginate_attr_class=None, **kwargs):
        if paginate_attr_class is None:
            paginate_attr_class = PaginateMixin

        if perpage is None:
            perpage = DEFAULT_PERPAGE

        if params is None:
            params = {}
        params.update(limit=perpage)

        resp = self._request(http_method, method, params=params, **kwargs)

        coll_keys = collection_key.split('.')
        if not nested_in(resp, coll_keys) and resp.get('total') == '0':
            nested_set(resp, coll_keys, PaginatedIterator(0, 0, iter([])))
            return resp

        attributes = paginate_attr_class(resp)

        if limit and limit < attributes.total:
            n_pages = min(attributes.total_pages, ceildiv(limit, perpage))
            pagerange = six.moves.range(2, n_pages + 1)
        else:
            pagerange = six.moves.range(2, attributes.total_pages + 1)

        def pagequery(page, http_method=http_method, method=method,
                      collection_key=collection_key, params=params,
                      kwargs=kwargs):
            params['page'] = page

            return self._request(http_method, method, params=params,
                                 collection_key=collection_key, **kwargs)

        thispage = _list_response(nested_get(resp, coll_keys))
        remaining_pages = chain.from_iterable(pagequery(page)
                                              for page in pagerange)
        iterator = chain(thispage, remaining_pages)

        nested_set(resp, coll_keys, PaginatedIterator(attributes.total_pages,
                                                      attributes.total,
                                                      iterator))

        return resp
