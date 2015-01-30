from six.moves import range
import six
from functools import wraps
import itertools
import logging
import hashlib
from datetime import datetime

from dateutil.parser import parse as dateparse


LOGGER = logging.getLogger('lastfm')


def parse_date(value):
    """
    Parse date from either a datestring or a dict with the datestring in the
    '#text' element.
    """
    if isinstance(value, datetime):
        return value
    elif isinstance(value, six.text_type):
        return dateparse(value)

    return dateparse(value['#text'])


def parse_image(value):
    """
    Parse image URL from a dict or a string
    """
    if isinstance(value, six.text_type):
        return value

    return value['#text']


def parse_bool_from_int(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, six.text_type):
        return bool(int(value))

    return bool(int(value['#text']))


def retry(attempts=2):
    """Function retry decorator"""

    if not attempts > 0:
        raise ValueError('Must have at least one atempt')

    def retry_dec(func):
        @wraps(func)
        def wrapper(*args, **kwArgs):
            last_error = None

            for attempt in range(attempts):
                try:
                    return func(*args, **kwArgs)
                except Exception as error:
                    LOGGER.debug('%s attempt #%d failed',
                                 func.__name__, attempt + 1)
                    last_error = error

            raise last_error
        return wrapper
    return retry_dec


def partition(coll, size):
    """Partition a collection into chunks"""
    coll = iter(coll)
    while True:
        chunk = list(itertools.islice(coll, size))
        if not chunk:
            break

        yield chunk


class Signer(object):

    NO_SIGN = frozenset(('api_sig', 'format'))

    def __init__(self, client):
        self._client = client

    @property
    def api_info(self):
        return self._client.api_info

    def sign(self, **params):
        """
        Return signature for the given parameters

        :param kwargs: Parameters/data to LastFM HTTP request
        :returns: API signature
        """
        if self.api_info.session_key is not None:
            params.update(sk=self.api_info.session_key)

        keystr = ''.join('{0}{1}'.format(key, params[key])
                         for key in sorted(params)
                         if key not in self.NO_SIGN)
        with_secret = keystr + self.api_info.secret
        return hashlib.md5(with_secret.encode('utf-8')).hexdigest()

    def __call__(self, **params):
        """
        Return signed HTTP parameters

        :param kwargs: Parameters/data to LastFM HTTP request
        :returns: params updated with `api_sig=<signature>`
        """
        params.update(api_sig=self.sign(**params))
        return params
