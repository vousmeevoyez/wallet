"""
    BNI OPG Response Object
    __________________
    module to handle HTTP Response from BNI OPG
"""
from task.bank.lib.response import HTTPResponse
from task.bank.lib.response import (
    FailedResponseError,
    ResponseError,
    DuplicateRequestError
)


class BNIOpgAuthResponse(HTTPResponse):
    """ HTTP Response represent BNI OPG Auth Response """

    def validate_status_code(self):
        """ override base http response so it raise Response Error
        instead of StatusCodeError """
        status_code = self.http_status
        if status_code != 200:
            # later should check whether status code valid or not !
            raise ResponseError("RESPONSE_FAILED", self.data)
        return True


class BNIOpgResponse(HTTPResponse):
    """ HTTP Response represent BNI OPG Response """

    @staticmethod
    def _check_response_code(response):
        """
            special function to check response code according to BNI response
        """
        for (key, value) in response.items():
            for (key, value) in value.items():
                if key == "parameters":
                    for key, value in value.items():
                        if key == "responseCode":
                            # check response code here
                            if value != "0001":
                                # mark request as failed
                                raise FailedResponseError(
                                    original_exception=response
                                )
                            elif value == "0007":
                                raise DuplicateRequestError(
                                    original_exception=response
                                )
        return True

    def validate_data(self):
        """ for bni response we need to decrypt it first before consume it """
        try:
            # first validate status any response
            self._check_response_code(self.data)
        except FailedResponseError as error:
            raise ResponseError("RESPONSE_FAILED", error.original_exception)
        except DuplicateRequestError as error:
            raise ResponseError("DUPLICATE_REQUEST", error.original_exception)
        # end try

    def validate(self):
        # only validate data ignore HTTP status code
        self.validate_data()
