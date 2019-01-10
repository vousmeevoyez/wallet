""" 
    AES Cipher MOdules
"""
import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

BLOCKSIZE = 16

PAD = lambda s: s + (BLOCKSIZE - len(s) % BLOCKSIZE) * chr(BLOCKSIZE - len(s) %
                                                           BLOCKSIZE)
UNPAD = lambda s: s[0: -s[-1]]

class AESCipher:
    """ Encryption using AES """

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode('utf-8')).digest()
    #end def

    def encrypt(self, raw):
        """ encrypt using AES """
        raw = PAD(raw)
        init_vector = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, init_vector)
        return base64.b64encode(init_vector + cipher.encrypt(raw.encode('utf8')))
    #end def

    def decrypt(self, encrypted_string):
        """ decrypt using AES """
        encrypted_string = base64.b64decode(encrypted_string)
        init_vector = encrypted_string[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, init_vector)
        decrypted = cipher.decrypt(encrypted_string[:16])
        print(decrypted)
        return UNPAD(decrypted)
    #end def
