"""
    Request
    __________________
    module to handle HTTP Request to all known API
"""
import json
import base64
import requests
import jwt

from app.config.external.bank import BNI_OPG

from task.bank.lib.request import HTTPRequest


class BNIOpgAuthRequest(HTTPRequest):

    username = BNI_OPG["USERNAME"]
    password = BNI_OPG["PASSWORD"]
    secret_key = BNI_OPG["SECRET_API_KEY"]
    client_id = BNI_OPG["CLIENT_NAME"]

    def create_signature(self, payload):
        """ generate jwt signature """
        signature = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return signature.decode("utf-8")

    # end def

    def setup_header(self, *args, **kwargs):
        auth_key = base64.b64encode(
            (BNI_OPG["USERNAME"] + ":" + BNI_OPG["PASSWORD"]).encode("utf-8")
        ).decode("utf-8")
        self._header["Authorization"] = "Basic {}".format(str(auth_key))
        self._header["Content-Type"] = "application/x-www-form-urlencoded"

    @property
    def payload(self):
        """ fetch request payload """
        return self._payload

    @payload.setter
    def payload(self, payload):
        """ set payload """
        # add clientId
        payload["clientId"] = self.client_id
        # add signature
        payload["signature"] = self.create_signature(payload)
        self._payload = payload


class BNIOpgRequest(BNIOpgAuthRequest):

    api_key = BNI_OPG["API_KEY"]

    def __init__(self, url, method):
        super().__init__(url, method)

    def setup_header(self, *args, **kwargs):
        self._header["x-api-key"] = self.api_key
        self._header["Content-Type"] = "application/json"

    def to_representation(self):
        """ represent the request as JSON """
        result = super().to_representation()
        result["data"] = json.dumps(result["data"])
        return result
