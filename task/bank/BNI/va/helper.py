import json

from task.bank.BNI.va.BniEnc3 import BniEnc, BNIVADecryptError


class DecryptError(Exception):
    pass


def encrypt(client_id, secret_key, data):
    return BniEnc().encrypt(json.dumps(data), client_id, secret_key).decode("utf-8")


def decrypt(client_id, secret_key, data):
    try:
        decrypted_data = BniEnc().decrypt(data, client_id, secret_key)
        return json.loads(decrypted_data)
    except BNIVADecryptError:
        raise DecryptError
