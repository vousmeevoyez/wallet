"""
    General Exceptions
    ________________
    Exceptions used in wallet.
"""
class ApiError(Exception):
    """ Error raised when some error occured when send data /
    return data from third party services """
    def __init__(self, msg, original_exception=None):
        super(ApiError, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
