""" 
    Remote Call
    __________________
    this is utility module that necessary to communicate to BNI Server to
    Encrypt and decrypt payload
"""
import json
import requests
import numpy as np

from app.api.bank.bni.utility import BniEnc3
from app.api.config import config

from app.api.exception.exceptions import ApiError

LOGGING_CONFIG = config.Config.LOGGING_CONFIG
BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)

def encrypt(client_id, secret_key, payload):
    """
        function to encrypt payload using bni custom library
        args :
            client_id -- BNI Client ID
            secret_key -- BNI Secret Key
            payload -- request payload
    """
    try:
        encrypyed_data = BniEnc3.BniEnc().encrypt(json.dumps(payload), client_id, secret_key)
    except:
        return None
    return encrypyed_data
#end def

def decrypt(client_id, secret_key, payload):
    """
        function to decrypt payload using bni custom library
        args :
            client_id -- BNI Client ID
            secret_key -- BNI Secret Key
            payload -- request payload
    """
    try:
        decrypted_data = BniEnc3.BniEnc().decrypt(payload, client_id, secret_key)
        return json.loads(decrypted_data)
    except:
        return None
#end def

def post(base_url, client_id, secret_key, data):
    """
        function to match the payload according to BNI and post it
        args:
            base_url -- BNI API URL
            client_id -- BNI Client Id
            secret_key -- BNI Secret Key
            data -- payload data
    """
    headers = {"content-type" : "application/json"}
    payload = {"client_id" : None, "data" : None}

    response = {"status" : 0, "data" : ""}

    payload["client_id"] = client_id
    payload["data"] = encrypt(client_id, secret_key, data)

    try:
        r = requests.post(base_url, #pylint: disable=invalid-name
                          data=json.dumps(payload, cls=MyEncoder),
                          headers=headers,
                          timeout=LOGGING_CONFIG["TIMEOUT"])
    except requests.exceptions.Timeout as err:
        raise ApiError("Request Timeout", err)
    except requests.exceptions.RequestException as err:
        raise ApiError("Unknown Exception", err)
    #end try

    result = r.json()

    status = result["status"]
    response["status"] = status
    try:
        data = result["data"]
        decrypted_data = decrypt(client_id, secret_key, data)

        response["data"] = decrypted_data
    except:
        msg = result["message"]
        response["data"] = msg
    #end try
    return response
#end def
