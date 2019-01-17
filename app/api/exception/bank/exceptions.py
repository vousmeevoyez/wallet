"""
    Bank Error
"""

class BankError(Exception):
    """ Base Class for Bank Error"""

class DecryptError(BankError):
    """ Error Raised when failed decrypt data from bank API """

class ServicesError(BankError):
    """ Error Raised when failed communicating with bank API """

class VirtualAccountError(BankError):
    """ Error Raised when related to VirtualAccount"""
