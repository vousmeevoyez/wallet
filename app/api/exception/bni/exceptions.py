"""
    Bank Error
"""

class BankError(Exception):
    """ Base Class for Bank Error"""

class DecryptError(BankError):
    """ Error Raised when failed decrypt data from bank API """

class ServicesError(BankError):
    """ Error Raised when failed communicating with bank API """
    def __init__(self, msg, original_exception=None):
    	super(ServicesError, self).__init__(msg, original_exception)
    	self.msg = msg
    	self.original_exception = original_exception

class VirtualAccountError(BankError):
    """ Error Raised when related to VirtualAccount"""
    def __init__(self, msg, original_exception=None):
    	super(VirtualAccountError, self).__init__(msg, original_exception)
    	self.msg = msg
    	self.original_exception = original_exception

class TokenError(BankError):
    """ Error raised related token """
    def __init__(self, original_exception):
        super(TokenError, self).__init__(original_exception)
        self.original_exception = original_exception

class InvalidInterbankAccountError(BankError):
    """ Error raised when trying to inquiry interbank account but not found"""
    def __init__(self, msg, original_exception=None):
        super(InvalidInterbankAccountError, self).__init__(msg,
                                                           original_exception)
        self.msg = msg
        self.original_exception = original_exception

class InterbankTransferError(BankError):
    """ Error raised when trying to interbank transfer but failed"""
    def __init__(self, msg, original_exception=None):
        super(InterbankTransferError, self).__init__(msg,
                                                     original_exception)
        self.msg = msg
        self.original_exception = original_exception

class InhouseTransferError(BankError):
    """ Error raised when trying to inhouse transfer but failed"""
    def __init__(self, msg, original_exception=None):
        super(InhouseTransferError, self).__init__(msg,
                                                     original_exception)
        self.msg = msg
        self.original_exception = original_exception