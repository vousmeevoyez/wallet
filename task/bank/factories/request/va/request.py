"""
    Request for BNI E=Collection
    ____________________________
"""
import json

from task.bank.lib.request import HTTPRequest
from app.config.external.bank import BNI_ECOLLECTION

from task.bank.lib.helper import encrypt, decrypt, DecryptError


class BNICreditEcollectionRequest(HTTPRequest):
    """ Class represent Credit BNI Ecollection Request """

    client_id = BNI_ECOLLECTION["CREDIT_CLIENT_ID"]
    secret_key = BNI_ECOLLECTION["CREDIT_SECRET_KEY"]

    def __init__(self):
        super().__init__()

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
        # include client id
        payload["client_id"] = self.client_id
        # need to add description
        payload["description"] = ""
        encrypted_data = encrypt(self.client_id, self.secret_key, payload)
        self._payload = {"client_id": self.client_id, "data": encrypted_data}

    def to_representation(self):
        """ represent the request as JSON """
        result = super().to_representation()
        result["data"] = json.dumps(result["data"])
        return result


class BNIDebitEcollectionRequest(BNICreditEcollectionRequest):
    """ Class represent BNI Ecollection Debit Request """

    client_id = BNI_ECOLLECTION["DEBIT_CLIENT_ID"]
    secret_key = BNI_ECOLLECTION["DEBIT_SECRET_KEY"]
