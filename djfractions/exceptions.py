class FractionError(Exception):
    pass


class InvalidFractionString(FractionError):
    """
    Raised when a string used for a fraction is not a valid format or representation
    of a fraction
    """

    pass


class NoHtmlUnicodeEntity(FractionError):
    """
    Raised when converting an unsupported fraction to an HTML entity
    from https://dev.w3.org/html5/html-author/charref
    """

    pass
