"""
    Helper  
    ______________
"""
from unittest.mock import Mock, patch

from task.test.base import BaseTestCase

from task.bank.BNI.va.helper import encrypt, decrypt
from app.config.external.bank import BNI_ECOLLECTION


class TestVAHelper(BaseTestCase):
    def test_encrypt(self):
        sample_data = {
            "type": "createbilling",
            "client_id": "99096",
            "trx_id": "56956153",
            "trx_amount": "100000",
            "billing_type": "d",
            "customer_name": "O3DO52",
            "customer_email": "",
            "customer_phone": "628495422781",
            "virtual_account": "9889909618606707",
            "datetime_expired": "2019-09-12 11:25:36",
        }

        encrypted = encrypt(
            BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
            BNI_ECOLLECTION["CREDIT_SECRET_KEY"],
            sample_data,
        )
        print(encrypted)

    def test_decrypt(self):
        sample_data = {
            "type": "createbilling",
            "client_id": "99096",
            "trx_id": "56956153",
            "trx_amount": "100000",
            "billing_type": "d",
            "customer_name": "O3DO52",
            "customer_email": "",
            "customer_phone": "628495422781",
            "virtual_account": "9889909618606707",
            "datetime_expired": "2019-09-12 11:25:36",
        }

        encrypted = encrypt(
            BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
            BNI_ECOLLECTION["CREDIT_SECRET_KEY"],
            sample_data,
        )

        decrypted = decrypt(
            BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
            BNI_ECOLLECTION["CREDIT_SECRET_KEY"],
            encrypted,
        )

        self.assertEqual(sample_data, decrypted)
