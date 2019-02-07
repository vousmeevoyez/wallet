"""
    General Exception
"""
class GeneralError(Exception):
    """ Base General Error """

class ApiError(GeneralError):
    """ Error raised when some error occured when send data /
    return data from third party services """
    def __init__(self, msg, original_exception=None):
        super(ApiError, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception

class SerializeError(GeneralError):
    """ Raised when serialize failed """
    def __init__(self, msg=None, details=None):
        super().__init__(msg, details)
        self.msg = msg
        self.details = details

class RecordNotFoundError(GeneralError):
    """ Raised when try query record but not found"""
    def __init__(self, msg, title=None):
        super().__init__(msg, title)
        self.msg = msg
        self.header = title

class CommitError(GeneralError):
    """ Raised when try commit a record but failed """
    def __init__(self, msg, original_exception=None, header=None, details=None):
        super().__init__(msg, original_exception, header)
        self.msg = msg
        self.header = header
        self.original_exception = original_exception
        self.details = details
