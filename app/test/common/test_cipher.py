""" 
    Test AES Cipher
"""

from app.test.base import BaseTestCase
from app.api.common.cipher import AESCipher

class TestAESCipher(BaseTestCase):
    """ AES Cipher Test Class"""

    def test_encrypt(self):
        """ test encrypt using aes """
        result = AESCipher('someveryverysecretkey').encrypt('Secret Message \
                                                            Kelvin')
        self.assertIsInstance(result, bytes)

    def test_decrypt(self):
        """ test decrypt using aes """
        text = "Here's my secret message"
        encrypted = AESCipher('someveryverysecretkey').encrypt(text)

        result = AESCipher('someveryverysecretkey').decrypt(encrypted)
        print(result)
        self.assertEqual(result, text)
