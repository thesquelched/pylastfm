from figgis import Config, Field
from six import text_type


class PaginatedAttributes(Config):

    page = Field(int)
    totalPages = Field(int)
    perPage = Field(int)
    total = Field(int)
    user = Field(text_type)


class PaginateMixin(Config):

    """
    Mixin that parses attributes required for pagination
    """

    attributes = Field(PaginatedAttributes, required=True, key='@attr')
