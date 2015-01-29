from lastfm import auth
from lastfm.util import Signer
from lastfm import constants


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


def authenticated(func):
    def wrapper(self, *args, **kwargs):
        if not self.api_info.authenticated:
            self.authenticate()

        return func(self, *args, **kwargs)


class LastFM(object):

    def __init__(self,
                 api_key,
                 api_secret,
                 username=None,
                 password=None,
                 password_hashed=None,
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
                                   password,
                                   hashed=password_hashed)

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
