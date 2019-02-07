"""
    Auth Error
"""

class AuthError(Exception):
    """ Base Class for Auth Error"""

class ParseTokenError(AuthError):
    """ Error raised when invalid token is used """
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

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

class TokenError(AuthError):
    """ Error raised when invalid token is used """
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

class InvalidCredentialsError(AuthError):
    """ Error raised when user login with invalid credentials """
    msg = "username / password is incorrect"
    title = "INVALID_CREDENTIALS"

class InvalidAuthorizationError(AuthError):
    """ error raised when authorization header failed """
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

class InsufficientScopeError(AuthError):
    """ error raised when user doesnt have permission to access this resourrces """
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

class MethodNotAllowedError(AuthError):
    """ error raised when user try use access token but resources only allowed
    refresh token"""
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

class FailedRevokedTokenError(AuthError):
    """ error raised when somethinig goes wrong when try logging out the token"""
    def __init__(self, msg, original_exception):
        super().__init__(msg)
        self.msg = msg
        self.original_exception = original_exception
        self.title = "REVOKE_TOKEN_FAILED"
