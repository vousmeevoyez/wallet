"""
    Virtual Account Error
"""

class VaError(Exception):
    """ Base Class for Virtual Account Error"""

class VaNotFoundError(VaError):
    """ raised when virtual account is not found"""
    msg = "Virtual account not found"
    title = "VA_NOT_FOUND"

class AlreadyExistVAError(VaError):
    """ raised when try creating virtual account but already have"""
    msg = "Virtual Account already existed"
    title = "VA_ALREADY_EXIST"