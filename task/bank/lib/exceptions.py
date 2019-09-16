""" 
    Base class for exceptiion
"""


class BaseError(Exception):
    """ Base Error for all classes """

    def __init__(self, message=None, original_exception=None):
        super().__init__(original_exception)
        self.original_exception = original_exception
        self.message = message
