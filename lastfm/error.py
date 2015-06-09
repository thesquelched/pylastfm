class LastfmError(Exception):
    """Base class for LastFM exceptions"""
    pass


class AuthenticationError(LastfmError):
    pass


class APIError(LastfmError):
    """Internal API error"""

    def __init__(self, code, message):
        msg = 'Error {0}: {1}'.format(code, message)
        super(APIError, self).__init__(msg)


class FileError(LastfmError, IOError):
    """Error reading/writing a file"""
    pass
