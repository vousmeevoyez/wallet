"""
    Auth Error
"""


class AuthError(Exception):
    """ Base Class for Auth Error"""


class RevokedTokenError(AuthError):
    """ Error raised when user try blacklisted token"""


class SignatureExpiredError(AuthError):
    """ Error raised when user try expired token"""

    def __init__(self, original_exception):
        super().__init__(original_exception)
        self.original_exception = original_exception


class InvalidTokenError(AuthError):
    """ Error raised when user try invalid token"""

    def __init__(self, original_exception):
        super().__init__(original_exception)
        self.original_exception = original_exception


class EmptyPayloadError(AuthError):
    """ Error raised when user try valid token with empty payload """
