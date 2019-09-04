"""
    Remote Call
    __________________
    this is utility module that necessary to communicate to BNI Server to
    Encrypt and decrypt payload
"""
import time
import json
import requests

from app.api import db

from app.api.models import ExternalLog

# const
from app.api.const import LOGGING

from task.bank.exceptions.general import ServicesFailed
from task.bank.BNI.utility.BniEnc3 import BniEnc

class DecryptError(Exception):
    """ decrypt error"""

def encrypt(client_id, secret_key, payload):
    """
        function to encrypt payload using bni custom library
        args :
            client_id -- BNI Client ID
            secret_key -- BNI Secret Key
            payload -- request payload
    """
    return BniEnc().encrypt(json.dumps(payload), client_id, secret_key)
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
        decrypted_data = BniEnc().decrypt(payload, client_id, secret_key)
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

    payload["client_id"] = client_id
    # decode bytes into string
    payload["data"] = encrypt(client_id, secret_key, data).decode("utf-8")
    try:
        # log everything before creating request
        log = ExternalLog(request=data, \
                          resource=LOGGING["BNI_ECOLLECTION"],
                          api_name=api_name,
                          api_type=LOGGING["OUTGOING"]
                          )
        db.session.add(log)

        # start measuring response time
        start_time = time.time()
        r = requests.post(base_url, #pylint: disable=invalid-name
                          #data=json.dumps(payload, cls=MyEncoder),
                          data=json.dumps(payload),
                          headers=headers)
        # save response time
        log.save_response_time(time.time() - start_time)
    except requests.exceptions.Timeout as error:
        raise ServicesFailed("TIMEOUT", error)
    except requests.exceptions.SSLError as error:
        raise ServicesFailed("SSL_ERROR", error)
    #end try

    response = r.json()
    try:
        decrypted_data = decrypt(client_id, secret_key, response["data"])
        # replace value
        response["data"] = decrypted_data
    except KeyError:
        # if we can't access response["data"] its potentially error
        log.set_status(False)
        response = response["message"]
        raise ServicesFailed("RESPONSE_ERROR", response)
    finally:
        log.save_response(response)
        db.session.commit()
    return response
#end def
