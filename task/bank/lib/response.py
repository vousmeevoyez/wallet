"""
    HTTP Response
    __________________
    base reusable class for various HTTP response
"""
from task.bank.lib.exceptions import BaseError


class StatusCodeError(BaseError):
    """ error raised related to status code error"""


class FailedResponseError(BaseError):
    """ Error raised when server return failed response code """


class InvalidResponseError(BaseError):
    """ Error raised when server return something that can be parsed
    by response """


class ResponseError(BaseError):
    """ Error raised when response error it can be failed / invalid """


class HTTPResponse:
    """ Wrap HTTP Response """

    def __init__(self, response):
        self._unpack_object(response)

    def _unpack_object(self, response):
        # unpack response header
        self.http_status = response.status_code
        # parse response and load it into property
        self.data = self._parse(response)

    @staticmethod
    def _extract(data):
        """ method to unwrap nested response so it much easy to consume """
        result = {}

        known_key = ["data"]
        for key in known_key:
            if key in data:
                result = data[key]
            else:
                result = data
            # end if
        # end for
        return result

    def _parse(self, response_object):
        try:
            response = response_object.json()
        except ValueError as error:
            raise InvalidResponseError("FAILED_DECODE_JSON", error)
        # end try
        return response

    def validate_status_code(self):
        """ execute status_code validation here """
        status_code = self.http_status
        if status_code != 200:
            # later should check whether status code valid or not !
            raise StatusCodeError("RESPONSE_ERROR", self.data)
        return True

    def validate_data(self):
        """ execute response validation here """
        return True

    def validate(self):
        """ wrapper method to validate everything """
        self.validate_status_code()
        self.validate_data()

    def to_representation(self):
        """ inteface method so client can consume the object properly """
        self.validate()
        return self.data
