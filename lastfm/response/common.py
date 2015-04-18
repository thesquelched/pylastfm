from figgis import Config, Field


def integer(value):
    return int(value) if value else 0


class PaginatedAttributes(Config):

    page = Field(integer, required=True)
    total_pages = Field(integer, key='totalPages', required=True)
    total = Field(integer, required=True)


class PaginateMixin(Config):

    """
    Mixin that parses attributes required for pagination
    """

    attributes = Field(PaginatedAttributes, required=True, key='@attr')
