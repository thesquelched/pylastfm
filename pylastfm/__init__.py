"""
Python LastFM bindings
"""

from .client import LastFM
from .error import LastfmError, AuthenticationError, APIError, FileError
from . import _version


__all__ = ['LastFM', 'LastfmError', 'AuthenticationError', 'APIError',
           'FileError']
__version__ = _version.__version__
