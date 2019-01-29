"""
    Auth Error
"""

class AuthError(Exception):
    """ Base Class for Auth Error"""

class InvalidAuthHeaderError(AuthError):
    """ Error raised when invalid authentication header used """

class EmptyAuthHeaderError(AuthError):
    """ Error raised when authenticaion header is empty"""
