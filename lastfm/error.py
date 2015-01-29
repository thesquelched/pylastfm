import six


class LastFMError(Exception):
    """Base class for LastFM exceptions"""
    pass


class AuthenticationError(LastFMError):
    pass


class HttpError(LastFMError):

    def __init__(self, code, *args):
        self.code = code
        if not args:
            args = (six.text_type(code), )

        super(HttpError, self).__init__(*args)
