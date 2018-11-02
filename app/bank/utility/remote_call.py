import requests
import json
import numpy as np

from app.bank.utility import BniEnc3
from app.config       import config

LOGGING_CONFIG = config.Config.LOGGING_CONFIG

class MyEncoder(json.JSONEncoder):
        def default(self, obj):
                if isinstance(obj, np.ndarray):
                        return obj.tolist()
                elif isinstance(obj, bytes):
                        return str(obj, encoding='utf-8')
                return json.JSONEncoder.default(self, obj)

def encrypt(client_id, secret_key, payload):
    try:
        encrypyed_data = BniEnc3.BniEnc().encrypt(json.dumps(payload), client_id, secret_key)
    except:
        return None
    return encrypyed_data
#end def

def decrypt(client_id, secret_key, payload):
    try:
        decrypted_data = BniEnc3.BniEnc().decrypt(payload, client_id, secret_key)
        return json.loads(decrypted_data)
    except:
        return None
#end def

def post(base_url, client_id, secret_key, data):
    headers = {  "content-type" : "application/json" }
    payload = { "client_id" : None, "data" : None    }

    response = { "status" : 0, "data" : ""}

    payload["client_id"] = client_id
    payload["data"     ] = encrypt(client_id, secret_key, data)

    try:
        r = requests.post(base_url,
                          data=json.dumps(payload, cls=MyEncoder),
                          headers=headers,
                          timeout=LOGGING_CONFIG["TIMEOUT"])

    except requests.exceptions.Timeout as err:
        response["status"] = 400
        response["data"  ] = str(err)
        return response

    result = r.json()

    status = result["status"]
    response["status"] = status
    try:
        data   = result["data"]
        decrypted_data = decrypt(client_id, secret_key, data)

        response["data"  ] = decrypted_data
    except:
        msg = result["message"]
        response["data"  ] = msg

    return response
#end def


