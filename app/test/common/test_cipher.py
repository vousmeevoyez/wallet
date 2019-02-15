""" 
    Test AES Cipher
"""

from app.test.base import BaseTestCase
from app.api.common.modules.cipher import AESCipher

from app.api.common.modules.cipher import DecryptError

class TestAESCipher(BaseTestCase):
    """ AES Cipher Test Class"""

    def test_encrypt(self):
        """ test encrypt using aes """
        result = AESCipher('someveryverysecretkey').encrypt('Secret Message \
                                                            Kelvin')
        self.assertIsInstance(result, bytes)

    def test_decrypt_success(self):
        """ test decrypt using aes """
        text = "Here's my secret message"
        encrypted = AESCipher('someveryverysecretkey').encrypt(text)

        result = AESCipher('someveryverysecretkey').decrypt(encrypted)
        self.assertEqual(result, text)

    def test_decrypt_failed(self):
        """ test decrypt using aes """
        with self.assertRaises(DecryptError):
            result =\
            AESCipher('someveryverysecretkey').decrypt("oIZfjX5HNAQQVeIKfnuF52VJ8wp472rjdsaljdlkajslkdjaljsdljaljdlasjljsadljW")
