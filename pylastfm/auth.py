from pylastfm.error import AuthenticationError, FileError

import six
import hashlib
import logging
import requests


LOGGER = logging.getLogger('lastfm')


class Authenticator(object):
    """Base class for LastFM authenticators"""

    def __init__(self, signer, api_info, username=None, password=None,
                 session_key=None):
        self._signer = signer
        self._api_info = api_info
        self._username = username
        self._password = password
        self._session_key = session_key

    @property
    def url(self):
        return self._api_info.url

    @property
    def api_key(self):
        return self._api_info.key

    @property
    def api_secret(self):
        return self._api_info.secret

    def sign(self, **params):
        return self._signer(**params)

    def session_key(self):
        raise NotImplementedError


class PasswordAuthToken(Authenticator):

    HASH_LOWER = frozenset('abcdef0123456789')
    HASH_UPPER = frozenset('ABCDEFG0123456789')
    HASH_LENGTH = 32

    def __init__(self, *args, **kwargs):
        self._hashed = kwargs.pop('hashed', None)

        super(PasswordAuthToken, self).__init__(*args, **kwargs)

    def session_key(self):
        """Get a LastFM session key"""

        # The user told us whether or not the password is hashed
        if self._hashed is not None:
            hashed_tries = (self._hashed,)
        else:
            guess = self._guess_password_hashed()
            hashed_tries = (guess, not guess)

        for hashed in hashed_tries:
            try:
                return self._authenticate_maybe_hashed(hashed)
            except AuthenticationError as exc:
                LOGGER.debug(
                    'Could not authenticate, assuming password %s hashed',
                    'was' if hashed else 'was not',
                    exc_info=exc)
                if hashed == hashed_tries[-1]:
                    raise

        assert False, "This should never be reached"

    def _authenticate_maybe_hashed(self, hashed):
        if hashed:
            pwhash = self._password
        else:
            pwhash = hashlib.md5(self._password.encode('utf-8')).hexdigest()

        authtoken = hashlib.md5(
            (self._username + pwhash).encode('utf-8')
        ).hexdigest()

        postdata = dict(
            method='auth.getMobileSession',
            username=self._username,
            authToken=authtoken,
            api_key=self.api_key,
            format='json',
        )
        LOGGER.debug('Authentication POST data: %s', postdata)

        try:
            resp = requests.post(
                self.url,
                data=self.sign(**postdata))
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            six.raise_from(AuthenticationError('Unable to get session'), exc)

        data = resp.json()
        if 'error' in data:
            raise AuthenticationError(data.get('message'))

        return resp.json()['session']['key']

    def _guess_password_hashed(self):
        """Return True if the password looks like a md5 hash"""
        pw = self._password
        chars = frozenset(pw)
        return len(pw) == 32 and (chars.issubset(self.HASH_LOWER) or
                                  chars.issubset(self.HASH_UPPER))


class Password(Authenticator):

    def session_key(self):
        postdata = self.sign(
            method='auth.getMobileSession',
            username=self._username,
            password=self._password,
            api_key=self.api_key,
            format='json',
        )
        LOGGER.debug('Authentication POST data: %s', postdata)

        try:
            resp = requests.post(
                self.url.replace('http://', 'https://'),
                data=postdata)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            six.raise_from(AuthenticationError('Unable to get session'), exc)

        data = resp.json()
        if 'error' in data:
            raise AuthenticationError(data.get('message'))

        return resp.json()['session']['key']


class SessionKey(Authenticator):

    def session_key(self):
        return self._session_key


class SessionKeyFile(Authenticator):

    def session_key(self):
        try:
            with open(self._session_key) as handle:
                return handle.read().strip()
        except IOError:
            raise FileError('Invalid/missing session key file: {0}'.format(
                self._session_key))


AUTH_METHODS = dict(
    password=Password,
    hashed_password=PasswordAuthToken,
    session_key=SessionKey,
    session_key_file=SessionKeyFile,
)
