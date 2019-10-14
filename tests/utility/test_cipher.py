""" 
    Test AES Cipher
"""
import pytest

from app.api.utility.modules.cipher import AESCipher

from app.api.utility.modules.cipher import DecryptError


""" AES Cipher Test Class"""

def test_encrypt():
    """ test encrypt using aes """
    result = AESCipher("someveryverysecretkey").encrypt(
        "Secret Message \
        Kelvin"
    )
    assert type(result) == bytes

def test_decrypt_success():
    """ test decrypt using aes """
    text = "Here's my secret message"
    encrypted = AESCipher("someveryverysecretkey").encrypt(text)

    result = AESCipher("someveryverysecretkey").decrypt(encrypted)
    assert result == text

def test_decrypt_failed():
    """ test decrypt using aes """
    with pytest.raises(DecryptError):
        result = AESCipher("someveryverysecretkey").decrypt(
            "oIZfjX5HNAQQVeIKfnuF52VJ8wp472rjdsaljdlkajslkdjaljsdljaljdlasjljsadljW"
        )
