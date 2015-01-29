from lastfm.error import AuthenticationError

import six
import hashlib
import logging
import requests


LOGGER = logging.getLogger('lastfm')


class Authenticator(object):
    """Base class for LastFM authenticators"""

    def __init__(self, signer, api_info):
        self._signer = signer
        self._api_info = api_info

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

    def session(self):
        raise NotImplementedError


class Password(Authenticator):

    HASH_LOWER = frozenset('abcdef0123456789')
    HASH_UPPER = frozenset('ABCDEFG0123456789')
    HASH_LENGTH = 32

    def __init__(self,
                 signer,
                 api_info,
                 username,
                 password,
                 hashed=None):
        super(Password, self).__init__(signer, api_info)

        self._username = username
        self._password = password
        self._hashed = hashed

    def session(self):
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

        raise AuthenticationError(
            'Could not authenticate with username/password')

    def _authenticate_maybe_hashed(self, hashed):
        if hashed:
            password = self._password
        else:
            password = hashlib.md5(self._password.encode('utf-8')).hexdigest()

        postdata = dict(
            username=self._username,
            password=password,
            api_key=self.api_key,
            format='json',
        )
        try:
            resp = requests.post(
                self.url + 'auth.getMobileSession',
                data=self.sign(**postdata))
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            six.raise_from(AuthenticationError('Unable to get session'), exc)

        return resp.json()['session']['key']

    def _guess_password_hashed(self):
        """Return True if the password looks like a md5 hash"""
        pw = self._password
        chars = frozenset(pw)
        return len(pw) == 32 and (chars.issubset(self.HASH_LOWER) or
                                  chars.issubset(self.HASH_UPPER))
