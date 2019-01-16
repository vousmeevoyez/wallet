"""
    AES Cipher MOdules
"""
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hashlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from app.api.exception.common.exceptions import DecryptError

class AESCipher:
    """ Encryption using AES """

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode('utf-8')).digest()
    #end def

    def encrypt(self, string):
        """ encrypt using AES """
        string = string.encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(string, AES.block_size))
        return urlsafe_b64encode(cipher.iv + ct_bytes)
    #end def

    def decrypt(self, string):
        """ decrypt using AES """
        try:
            decoded_string = urlsafe_b64decode(string)
        except:
            raise DecryptError
        #end try
        init_vector = decoded_string[:AES.block_size]
        cipher_text = decoded_string[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, init_vector)
        try:
            return unpad(cipher.decrypt(cipher_text), AES.block_size).decode('utf-8')
        except:
            raise DecryptError
    #end def
#end class
