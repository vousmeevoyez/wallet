"""
    Auth Error
"""

class AuthError(Exception):
    """ Base Class for Auth Error"""

class ParseTokenError(AuthError):
    """ Error raised when invalid token is used """
    def __init__(self, msg):
        super(ParseTokenError, self).__init__(msg)
        self.msg = msg

class RevokedTokenError(AuthError):
    """ Error raised when user try blacklisted token"""

class SignatureExpiredError(AuthError):
    """ Error raised when user try expired token"""

class InvalidTokenError(AuthError):
    """ Error raised when user try invalid token"""

class EmptyPayloadError(AuthError):
    """ Error raised when user try valid token with empty payload """

class TokenError(AuthError):
    """ Error raised when invalid token is used """
    def __init__(self, msg):
        super(TokenError, self).__init__(msg)
        self.msg = msg
