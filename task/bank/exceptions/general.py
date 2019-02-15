"""
    Task General Exceptions
"""
class BaseError(Exception):
    """ base error"""

class DecryptError(BaseError):
    """ raised when failed decrypt something"""

class ServicesFailed(BaseError):
    """ raised when something goes wrong trying to hit 3rd party API either
    timeout or response error"""
    def __init__(self, message, original_exception):
        super().__init__(message, original_exception)
        self.message = message
        self. original_exception = original_exception

class RemoteCallError(BaseError):
    """ raised when remote call error """
    def __init__(self, original_exception):
        super().__init__(original_exception)
        self. original_exception = original_exception

class ApiError(BaseError):
    """ raised when API call failed """
    def __init__(self, original_exception):
        super().__init__(original_exception)
        self.original_exception = original_exception
