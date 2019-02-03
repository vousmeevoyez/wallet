import json

from app.test.base              import BaseTestCase
from app.api.bank.bni.utility   import remote_call
from app.config             import config

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

class TestUtil(BaseTestCase):

    def test_generate_mockup_deposit_callback(self):
        data = {
            "virtual_account"           : "9889909825214406",
            "customer_name"             : "jennie",
            "trx_id"                    : "669827448",
            "trx_amount"                : "0",
            "payment_amount"            : "50000",
            "cumulative_payment_amount" : "50000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-12-20 11:16:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }
        print("------------------deposit----------------------")
        print(json.dumps(expected_value))
        print("------------------deposit----------------------")

    def test_generate_mockup_withdraw_callback(self):
        # CREATE ENCRYPYED WITHDRAW MOCKUP RESPONSE
        data = {
            "virtual_account"           : "9889909825214406",
            "customer_name"             : "jennie",
            "trx_id"                    : "669827448",
            "trx_amount"                : "0",
            "payment_amount"            : "-50000",
            "cumulative_payment_amount" : "-50000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-12-20 13:05:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        print("------------------withdraw----------------------")
        print(json.dumps(expected_value))
        print("------------------withdraw----------------------")
