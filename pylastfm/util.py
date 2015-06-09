import six
from functools import wraps
import itertools
import logging
import hashlib
from datetime import datetime
from dateutil.parser import parse as dateparse


LOGGER = logging.getLogger('lastfm')


NOT_SPECIFIED = object()


def retry(attempts=2):
    """Function retry decorator"""

    if not attempts > 0:
        raise ValueError('Must have at least one atempt')

    def retry_dec(func):
        @wraps(func)
        def wrapper(*args, **kwArgs):
            last_error = None

            for attempt in six.moves.range(attempts):
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
        if self.api_info.session_key:
            params.update(sk=self.api_info.session_key)

        LOGGER.debug('Signing parameters: %s', params)
        keystr = ''.join('{0}{1}'.format(key, params[key])
                         for key in sorted(params)
                         if params[key] is not None and
                         key not in self.NO_SIGN)

        with_secret = keystr + self.api_info.secret
        LOGGER.debug('Pre-hashed signature: %s', with_secret)

        return hashlib.md5(with_secret.encode('utf-8')).hexdigest()

    def __call__(self, **params):
        """
        Return signed HTTP parameters

        :param kwargs: Parameters/data to LastFM HTTP request
        :returns: params updated with `api_sig=<signature>`
        """
        params.update(api_sig=self.sign(**params))
        if self.api_info.session_key:
            params.update(sk=self.api_info.session_key)

        return params


class PaginatedIterator(object):

    def __init__(self, pages, total, iterator):
        self._pages = max(1, pages)
        self._total = total
        self._iterator = iterator

    def __iter__(self):
        return self._iterator

    def next(self):
        return six.next(self._iterator)

    __next__ = next

    def __len__(self):
        return self._total

    @property
    def pages(self):
        return self._pages

    def __repr__(self):
        return '<PaginatedIterator({} pages)>'.format(self._pages)

    def map(self, func):
        """Return a new PaginatedIterator generated from mapping the function
        to this iterator"""
        return PaginatedIterator(
            self._pages,
            self._total,
            (func(item) for item in self._iterator))


def unix_timestamp(date):
    return int((date - datetime(1970, 1, 1)).total_seconds())


def query_date(value):
    """Format value into a suitable date for the API"""
    if value is None:
        return value

    if isinstance(value, datetime):
        return unix_timestamp(value)

    # See if it's already a UNIX timestamp
    try:
        date = datetime.fromtimestamp(int(value))
        assert date >= datetime.fromtimestamp(0)
        return unix_timestamp(date)
    except (ValueError, AssertionError):
        pass

    # Try to parse a datestring
    try:
        return unix_timestamp(dateparse(value))
    except ValueError:
        raise ValueError('Invalid timestamp: {}'.format(value))


def keywords(*keys, **defaultkeys):
    """Decorator that helps handle functions that have a variable number of
    keyword arguments in the function signature, but only expect certain
    keywords. Checks that the keyword argument dictionary doesn't contain
    extraneous keywords. Also injects key defaults into kwargs"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            extra_kwargs = set(kwargs) - set(defaultkeys).union(keys)
            if extra_kwargs:
                raise TypeError(
                    "{0}() got an unexpected keyword argument: '{1}'".format(
                        func.__name__, six.next(iter(kwargs))))

            for key in keys:
                if key not in kwargs:
                    kwargs[key] = None
            for key, value in defaultkeys.items():
                if key not in kwargs:
                    kwargs[key] = value

            return func(*args, **kwargs)
        return wrapper
    return decorator


def nested_get(data, keys, default=NOT_SPECIFIED):
    """
    Return data[key1][key2]...[keyN]. Optionally takes a default for if any of
    the keys in the sequence are missing. Unlike `dict.get`, this will throw
    """
    for key in keys:
        try:
            data = data[key]
        except KeyError:
            if default is NOT_SPECIFIED:
                raise
            else:
                return default

    return data


def nested_set(data, keys, value):
    """
    Set `data[key1][key2]...[keyN] = value`
    """
    if not keys:
        raise TypeError('At least one key is required')

    for key in keys[:-1]:
        data = data[key]

    data[keys[-1]] = value


def nested_in(data, keys):
    """
    Check if a series of keys is located in a nested dict
    """
    for key in keys:
        try:
            data = data[key]
        except KeyError:
            return False

    return True


def ceildiv(a, b):
    """Integer ceiling division"""
    return -(-a // b)
