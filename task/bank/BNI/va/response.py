"""
    BNI Response Object
    __________________
    module to handle HTTP Response from BNI Va
"""
import json

from task.bank.BNI.va.BniEnc3 import BniEnc, BNIVADecryptError

from app.config.external.bank import BNI_ECOLLECTION
from task.bank.lib import (
    HTTPResponse,
    InvalidResponseError,
    FailedResponseError,
    ResponseError,
)


class BNIEcollectionCreditResponse(HTTPResponse):
    """ HTTP Response represent BNI Credit Ecollection Response """

    client_id = BNI_ECOLLECTION["CREDIT_CLIENT_ID"]
    secret_key = BNI_ECOLLECTION["CREDIT_SECRET_KEY"]

    def decrypt(self, response):
        """ method to decrypt BNI response """
        result = {}
        try:
            decrypted_data = BniEnc().decrypt(
                response["data"], self.client_id, self.secret_key
            )
            result = json.loads(decrypted_data)
        except BNIVADecryptError:
            raise InvalidResponseError(
                original_exception="Failed decrypt BNI VA Response"
            )
        return result

    @staticmethod
    def validate_bni_status(response):
        """  method to check BNI Status """
        if response["status"] != "000":
            error_message = response["message"]
            raise FailedResponseError(original_exception=error_message)
        return response

    def validate_data(self):
        """ for bni response we need to decrypt it first before consume it """
        try:
            # first validate status any response
            response = self.validate_bni_status(self.data)
            # second decrypt or raise error
            decrypted_data = self.decrypt(response)
        except FailedResponseError as error:
            raise ResponseError("RESPONSE_ERROR", error.original_exception)
        except InvalidResponseError as error:
            raise ResponseError("INVALID_RESPONSE", error.original_exception)
        # end try
        self.data = decrypted_data
        return decrypted_data


class BNIEcollectionDebitResponse(BNIEcollectionCreditResponse):
    """ HTTP Response represent BNI DEBIT Ecollection Response """

    client_id = BNI_ECOLLECTION["DEBIT_CLIENT_ID"]
    secret_key = BNI_ECOLLECTION["DEBIT_SECRET_KEY"]
