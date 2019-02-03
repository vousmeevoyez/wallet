"""
    Virtual Account Error
"""

class VaError(Exception):
    """ Base Class for Virtual Account Error"""

class VirtualAccountCreationError(VaError):
    """ Error raised when failed adding Virtual Account """
    def __init__(self, original_exception):
        super(VirtualAccountCreationError, self).__init__(original_exception)
        self.original_exception = original_exception

class AlreadyExistVAError(VaError):
    """ raised when try adding va but already have va binded to his wallet """
