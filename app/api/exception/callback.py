"""
    Callback Exceptions
"""
class BaseError(Exception):
    """Base Error Class """

class InvalidCallbackError(BaseError):
    """ Error that potentially raised because failed to decrypt callback from
    bank"""
    msg = "Invalid Callback"
    title = "INVALID_CALLBACK"
