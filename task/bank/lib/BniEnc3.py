#!/opt/local/bin/python

import time
import json
import string
import math
import base64


class BNIVADecryptError(Exception):
    """ error raised when BNI Encryption/ Decryption Failed"""


class BniEnc:
    TIME_DIFF_LIMIT = 480

    @staticmethod
    def encrypt(json_data, cid, secret):
        t = str(int(time.time()))[::-1]
        return BniEnc.doubleEncrypt(t + "." + json_data, cid, secret)

    @staticmethod
    def decrypt(hashed_string, cid, secret):
        parseStr = BniEnc.doubleDecrypt(hashed_string, cid, secret)
        data = parseStr.split(".", 1)
        if len(data) == 2:
            strrevtime = data[0][::-1]
            try:
                if BniEnc.tsDiff(int(strrevtime)):
                    return data[1]
            except ValueError:
                raise BNIVADecryptError

        raise BNIVADecryptError

    @staticmethod
    def tsDiff(ts):
        return math.fabs(ts - time.time()) <= BniEnc.TIME_DIFF_LIMIT

    @staticmethod
    def doubleEncrypt(stringObj, cid, secret):
        result = ""
        result = BniEnc.enc(stringObj, cid)
        result = BniEnc.enc(result, secret)
        # result = result.encode('base64').rstrip('=')
        # result = result.translate(str.maketrans('+/', '-_'))
        result = bytes(result, "utf-8")
        result = base64.b64encode(result)
        return result

    @staticmethod
    def enc(string, key):
        result = ""
        strls = len(string)
        strlk = len(key)
        for i in range(0, strls):
            char = string[i : i + 1]
            st = (i % strlk) - 1
            xlen = None if st < 0 else st + 1
            keychar = key[st:xlen]
            char = chr((ord(char) + ord(keychar)) % 128)
            result += char

        return result

    @staticmethod
    def doubleDecrypt(string, cid, secret):
        ceils = math.ceil(len(string) / 4.0) * 4
        while len(string) < ceils:
            string += "="
        string = string.replace("-", "+").replace("_", "/")
        result = base64.b64decode(string)
        result = BniEnc.dec(result, cid)
        result = BniEnc.dec(result, secret)
        return result

    @staticmethod
    def dec(string, key):
        result = ""
        strls = len(string)
        strlk = len(key)
        for i in range(0, strls):
            char = string[i : i + 1]
            st = (i % strlk) - 1
            xlen = None if st < 0 else st + 1
            keychar = key[st:xlen]
            char = chr((ord(char) - ord(keychar) + 256) % 128)
            result += char

        return result
