"""
    BNI E-Collection Helper
    ________________________
"""
from datetime import datetime
import functools
import json
import random

from task.bank.lib.BniEnc3 import BniEnc, BNIVADecryptError


class DecryptError(Exception):
    """ error raised to encapsulate decrypt error from BNI """


def encrypt(client_id, secret_key, data):
    """ encrypt data using BNI Client ID + Secret + data """
    return BniEnc().encrypt(
        json.dumps(data),
        client_id,
        secret_key
    ).decode("utf-8")


def decrypt(client_id, secret_key, data):
    """ decrypt data using BNI Client ID + Secret + data """
    try:
        decrypted_data = BniEnc().decrypt(data, client_id, secret_key)
        return json.loads(decrypted_data)
    except BNIVADecryptError:
        raise DecryptError


def opg_extract_error(obj):
    """ extract error from BNI OPG Response format """
    error_message = ""
    if isinstance(obj.original_exception, dict):
        for key, value in obj.original_exception.items():
            for key, value in value.items():
                if key == "parameters":
                    for key, value in value.items():
                        if key == "errorMessage":
                            error_message = value
                        # end if
                    # end for
                # end if
            # end for
        # end for
    # end if
    return error_message


def extract_error(obj):
    try:
        key = obj.original_exception["response"]
    except KeyError:
        error = opg_extract_error(obj)
    except:
        error = obj.message
    return error


@functools.lru_cache(maxsize=128)
def generate_ref_number(destination, amount=None):
    """ generate reference number matched to BNI format"""
    now = datetime.utcnow()
    # first 8 digit is date
    value_date = now.strftime("%Y%m%d%H%M")
    randomize = random.randint(1, 99)

    end_fix = str(destination)[:8]
    if amount is not None:
        end_fix = str(destination)[:4] + str(amount)[:4]

    return str(value_date) + str(end_fix) + str(randomize)
