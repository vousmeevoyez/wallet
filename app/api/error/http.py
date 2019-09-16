"""
    HTTP ERROR
"""


class HTTPError(Exception):
    """ base error class """

    def __init__(self, error, code, message, details):
        super().__init__(error, code, message, details)
        self.error = error
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self):
        """
	        Call this in the the error handler to serialize the
	        error for the json-encoded http response body.
        """
        error_response = {"error": self.error, "message": self.message}
        if self.details is not None:
            error_response["details"] = self.details
        # end if
        return error_response

    # end def


# end class


class BadRequest(HTTPError):
    """ base http error class for any bad request"""

    def __init__(self, error=None, message=None, details=None):
        super(HTTPError, self).__init__(error, message, details)
        self.code = 400

        if error is None:
            self.error = "BAD_REQUEST"
        else:
            self.error = error
        # end if

        self.message = message
        self.details = details

    # end def


# end class


class RequestNotFound(HTTPError):
    """ base http error class for any resource not found"""

    def __init__(self, error=None, message=None, details=None):
        super(HTTPError, self).__init__(error, message, details)
        self.code = 404

        if error is None:
            self.error = "REQUEST_NOT_FOUND"
        else:
            self.error = error
        # end if
        self.message = message
        self.details = details

    # end def


# end class


class UnprocessableEntity(HTTPError):
    """ base http error class for any resource not found"""

    def __init__(self, error=None, message=None, details=None):
        super(HTTPError, self).__init__(error, message, details)
        self.code = 422

        if error is None:
            self.error = "UNPROCESSABLE_ENTITY"
        else:
            self.error = error
        # end if
        self.message = message
        self.details = details

    # end def


# end class


class Unauthorized(HTTPError):
    """ base http error class for unauthorized access"""

    def __init__(self, error=None, message=None, details=None):
        super(HTTPError, self).__init__(error, message, details)
        self.code = 401

        if error is None:
            self.error = "UNAUTHORIZED"
        else:
            self.error = error
        # end if
        self.message = message
        self.details = details


# end class


class InsufficientScope(HTTPError):
    """ base http error class for insufficient scope """

    def __init__(self, error=None, message=None, details=None):
        super(HTTPError, self).__init__(error, message, details)
        self.code = 403

        if error is None:
            self.error = "INSUFFICIENT_SCOPE"
        else:
            self.error = error
        # end if
        self.message = message
        self.details = details

    # end def


# end class


class MethodNotAllowed(HTTPError):
    """ base http error class for insufficient scope """

    def __init__(self, message=None):
        super(HTTPError, self).__init__(message)
        self.code = 405
        self.error = "METHOD_NOT_ALLOWED"
        self.message = message
        self.details = None

    # end def


# end class
