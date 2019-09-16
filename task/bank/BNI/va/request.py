"""
    BNI Request Object
    __________________
    module to handle HTTP Request to BNI Va
"""
import json

from task.bank.BNI.va.helper import encrypt, decrypt, DecryptError

from task.bank.lib import HTTPRequest

from app.config.external.bank import BNI_ECOLLECTION


class BNIEcollectionCreditRequest(HTTPRequest):
    """ BNI VA CREDIT REQUEST  """

    client_id = BNI_ECOLLECTION["CREDIT_CLIENT_ID"]
    secret_key = BNI_ECOLLECTION["CREDIT_SECRET_KEY"]

    def __init__(self, url, method):
        super().__init__(url, method)

    @property
    def payload(self):
        """ fetch request payload """
        try:
            decrypted_data = decrypt(
                self.client_id, self.secret_key, self._payload["data"]
            )
        except DecryptError:
            raise DecryptError
        else:
            # switch encrypted with decrypted
            self._payload["data"] = decrypted_data
        return self._payload

    @payload.setter
    def payload(self, payload):
        """ set payload """
        encrypted_data = encrypt(self.client_id, self.secret_key, payload)
        self._payload = {"client_id": self.client_id, "data": encrypted_data}

    def to_representation(self):
        """ represent the request as JSON """
        result = super().to_representation()
        result["data"] = json.dumps(result["data"])
        return result


class BNIEcollectionDebitRequest(BNIEcollectionCreditRequest):
    """ BNI VA DEBIT REQUEST OBJECT """

    client_id = BNI_ECOLLECTION["DEBIT_CLIENT_ID"]
    secret_key = BNI_ECOLLECTION["DEBIT_SECRET_KEY"]
