""" 
    Remote Call
    __________________
    this is utility module that necessary to communicate to BNI Server to
    Encrypt and decrypt payload
"""
import time
import json
import requests
import numpy as np

from app.api import db

from app.api.bank.bni.utility import BniEnc3

from app.api.models import ExternalLog

from app.api.exception.exceptions import ApiError
from app.api.exception.bank.exceptions import DecryptError

from app.api.config import config

LOGGING_CONFIG = config.Config.LOGGING_CONFIG
BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)
#end class

def encrypt(client_id, secret_key, payload):
    """
        function to encrypt payload using bni custom library
        args :
            client_id -- BNI Client ID
            secret_key -- BNI Secret Key
            payload -- request payload
    """
    return BniEnc3.BniEnc().encrypt(json.dumps(payload), client_id, secret_key)
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
        raise DecryptError
#end def

def post(api_name, base_url, client_id, secret_key, data):
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
        # log everything before creating request
        log = ExternalLog(request=data, \
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=api_name,
                          api_type=LOGGING_CONFIG["OUTGOING"]
                          )
        db.session.add(log)

        # start measuring response time
        start_time = time.time()
        r = requests.post(base_url, #pylint: disable=invalid-name
                          data=json.dumps(payload, cls=MyEncoder),
                          headers=headers,
                          timeout=LOGGING_CONFIG["TIMEOUT"])
        # save response time
        log.save_response_time(time.time() - start_time)
    except requests.exceptions.Timeout as err:
        raise ApiError("TIMEOUT", err)
    except requests.exceptions.RequestException as err:
        raise ApiError("UNKNOWN", err)
    #end try

    result = r.json()

    status = result["status"]
    response["status"] = status
    try:
        decrypted_data = decrypt(client_id, secret_key, result["data"])
        response["data"] = decrypted_data
    except KeyError:
        log.set_status(False)
        response["data"] = result["message"]
        raise ApiError("RESPONSE_FAILED", result["message"])
    finally:
        log.save_response(response["data"])
    return response
#end def
