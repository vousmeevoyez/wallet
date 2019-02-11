"""
    Task General Exceptions
"""
class BaseError(Exception):
    """ base error"""

class DecryptError(BaseError):
    """ raised when failed decrypt something"""

class ServicesTimeout(BaseError):
    """ raised when timeout """

class ServicesFailed(BaseError):
    """ raised when services return failed response"""
