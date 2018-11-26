import sys
import unittest
from unittest.mock import Mock, patch
import json

sys.path.append("../")
sys.path.append("../app")

# FLASK

from app                import create_app, db
from app.config         import config
from app.models         import User, Wallet, VirtualAccount, Transaction
from app.bank.utility   import remote_call

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

class TestConfig(config.Config):

    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class TestCallbackRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()

        self.mock_post_patcher = patch("app.bank.utility.remote_call.requests.post")
        self.mock_post = self.mock_post_patcher.start()

        self._init_test()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.mock_post_patcher.stop()

    def _init_test(self):
        # SET MOCKUP RESPONSE FOR CREATING VA
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("jessica", "jessica", "089219644324", "jessica@modana.id", "password", "123456", "1")
        response = result.get_json()

        self.wallet_id = response["data"]["wallet_id"]

        # get access token
        response = self._request_token("jessica", "password")
        result = response.get_json()
        self.access_token = result["data"]["access_token"]

        self.va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).first()

        # CREATE ENCRYPYED DEPOSIT MOCKUP RESPONSE
        data = {
            "virtual_account"           : "9889909813169928",
            "customer_name"             : "Rose",
            "trx_id"                    : "227473614",
            "trx_amount"                : "0",
            "payment_amount"            : "50000",
            "cumulative_payment_amount" : "50000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }
        #print(json.dumps(expected_value))

        # SET MOCKUP RESPONSE FOR UPDATING VA
        expected_value = {
            "status" : "000",
            "message": {'type': 'updatebilling', 'client_id': '99099', 'trx_id': '627493687', 'trx_amount': '1000', 'customer_name': 'Kelvin', 'datetime_expired': '2017-10-29 06:39:27'}
        }
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

    """
        HELPER
    """

    def _callback_deposit(self, json):
        return self.client.post(
            '/callback/deposit',
            json=json
        )

    def _callback_withdraw(self, json):
        return self.client.post(
            '/callback/withdraw',
            json=json
        )

    def _register_user(self, username, name, msisdn, email, password, pin, role):
        return self.client.post(
            '/user/register',
            data=dict(
                username=username,
                name=name,
                msisdn=msisdn,
                email=email,
                password=password,
                pin=pin,
                role=role
            )
        )

    def _check_balance(self, access_token, wallet_id, pin):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            '/wallet/balance',
            data=dict(
                wallet_id=wallet_id,
                pin=pin
            ),
            headers=headers
        )

    def _request_token(self, username, password):
        return self.client.post(
            '/auth/request_token',
            data=dict(
                username=username,
                password=password
            )
        )



    """
        DEPOSIT CALLBACK
    """
    def test_callback_deposit_success(self):
        data = {
            "virtual_account"           : str(self.va.id),
            "customer_name"             : str(self.va.name),
            "trx_id"                    : str(self.va.trx_id),
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "50000",
            "cumulative_payment_amount" : "50000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_deposit(expected_value)
        response = result.get_json()
        print(response)

        self.assertEqual( response["status"], "000")

        # make sure balance injected successfully
        result = self._check_balance(self.access_token, self.wallet_id, "123456")
        response = result.get_json()
        self.assertEqual( response["data"]["balance"], int(data["payment_amount"]))

        transaction = Transaction.query.all()
        print(transaction)

    def test_callback_deposit_failed_min_deposit(self):
        data = {
            "virtual_account"           : str(self.va.id),
            "customer_name"             : str(self.va.name),
            "trx_id"                    : str(self.va.trx_id),
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "1",
            "cumulative_payment_amount" : "1",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_deposit(expected_value)
        response = result.get_json()

        self.assertEqual( response["status"], "400")

    def test_callback_deposit_failed_max_deposit(self):
        data = {
            "virtual_account"           : str(self.va.id),
            "customer_name"             : str(self.va.name),
            "trx_id"                    : str(self.va.trx_id),
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "99999999999999999",
            "cumulative_payment_amount" : "99999999999999999",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_deposit(expected_value)
        response = result.get_json()

        self.assertEqual( response["status"], "400")

    def test_callback_deposit_failed_va_not_found(self):
        data = {
            "virtual_account"           : "9889909910336282",
            "customer_name"             : str(self.va.name),
            "trx_id"                    : "123456",
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "50000",
            "cumulative_payment_amount" : "50000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_deposit(expected_value)
        response = result.get_json()

        self.assertEqual( response["status"], "404")

    def test_callback_withdraw_success(self):
        db.session.begin()
        start_balance = 100000
        # hard inject the balance first
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        wallet.add_balance(start_balance)
        db.session.commit()

        data = {
            "virtual_account"           : str(self.va.id),
            "customer_name"             : str(self.va.name),
            "trx_id"                    : str(self.va.trx_id),
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "-59999",
            "cumulative_payment_amount" : "-59999",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_withdraw(expected_value)
        response = result.get_json()
        self.assertEqual( response["status"], "000")

        # make sure balance deducted successfully
        result = self._check_balance(self.access_token, self.wallet_id, "123456")
        response = result.get_json()
        self.assertEqual( response["data"]["balance"], start_balance + int(data["payment_amount"]))

        transaction_list = Transaction.query.all()
        for item in transaction_list:
            print(item.notes)

    def test_callback_withdraw_failed_min_amount(self):
        db.session.begin()
        start_balance = 100000
        # hard inject the balance first
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        wallet.add_balance(start_balance)
        db.session.commit()

        data = {
            "virtual_account"           : str(self.va.id),
            "customer_name"             : str(self.va.name),
            "trx_id"                    : str(self.va.trx_id),
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "-1",
            "cumulative_payment_amount" : "-1",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_withdraw(expected_value)
        response = result.get_json()

        self.assertEqual( response["status"], "400")

    def test_callback_withdraw_failed_max_amount(self):
        db.session.begin()
        start_balance = 100000
        # hard inject the balance first
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        wallet.add_balance(start_balance)
        db.session.commit()

        data = {
            "virtual_account"           : str(self.va.id),
            "customer_name"             : str(self.va.name),
            "trx_id"                    : str(self.va.trx_id),
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "-99999999999999",
            "cumulative_payment_amount" : "-99999999999999",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_withdraw(expected_value)
        response = result.get_json()

        self.assertEqual( response["status"], "400")

    def test_callback_withdraw_failed_va_not_found(self):
        db.session.begin()
        start_balance = 100000
        # hard inject the balance first
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        wallet.add_balance(start_balance)
        db.session.commit()

        data = {
            "virtual_account"           : "9889909910336282",
            "customer_name"             : str(self.va.name),
            "trx_id"                    : str(self.va.trx_id),
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "-99999",
            "cumulative_payment_amount" : "-99999",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_withdraw(expected_value)
        response = result.get_json()

        self.assertEqual( response["status"], "404")

if __name__ == "__main__":
    unittest.main(verbosity=2)
