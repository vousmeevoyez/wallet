import requests
import json
import numpy as np


from utility import BniEnc_3

class MyEncoder(json.JSONEncoder):
        def default(self, obj):
                if isinstance(obj, np.ndarray):
                        return obj.tolist()
                elif isinstance(obj, bytes):
                        return str(obj, encoding='utf-8')
                return json.JSONEncoder.default(self, obj)

def encrypt(client_id, secret_key, payload):
    return BniEnc_3.BniEnc().encrypt(json.dumps(payload), client_id, secret_key)
#end def

def decrypt(client_id, secret_key, payload):
    return BniEnc_3.BniEnc().decrypt(payload, client_id, secret_key)
#end def

def post(base_url, client_id, secret_key, data):
    headers = {  "content-type" : "application/json" }
    payload = { "client_id" : None, "data" : None    }

    try:
        payload["client_id"] = client_id
        payload["data"     ] = encrypt(client_id, secret_key, data)

        r = requests.post( base_url, data=json.dumps(payload, cls=MyEncoder), headers=headers)
        if (r.json().get('message')):
            return r.text

        response = r.json().get("data")

    except Exception as e:
        print(traceback.format_exc())
        return e

    return decrypt(client_id, secret_key, response)
#end def


