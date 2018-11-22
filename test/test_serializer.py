import sys
import unittest

sys.path.append("../")
sys.path.append("../app")

from datetime import datetime, timedelta

from app            import create_app
from app.serializer import ApiKeySchema, UserSchema, WalletSchema, TransactionSchema, CallbackSchema
from app.config     import config

from marshmallow import ValidationError

now = datetime.utcnow()

class TestApiKeySchema(unittest.TestCase):
    def test_serializer(self):
        #with self.assertRaises(ValidationError) as context:
        #    ApiKeySchema().load({ "label" : 1234, "name" : "name"})
        #self.assertTrue("{'label': ['Not a valid string.']}" in str(context.exception))

        result, errors = ApiKeySchema().load({ "label" : "test", "name" : "name", "expiration" : 0, "username" : "jennie", "password" : "password"})
        self.assertEqual( errors, {'expiration': ['Invalid Expiration, Cannot be less or equal 0']} )

        result, errors = ApiKeySchema().load({ "label" : 1234, "name" : "name", "expiration" : 1, "username" : "jennie", "password" : "password"})
        self.assertEqual( errors, {'label': ['Not a valid string.']})

        result, errors = ApiKeySchema().load({ "label" : 1234, "name" : 1234, "expiration" : 1, "username" : "jennie", "password" : "password"})
        self.assertEqual( errors, {'label': ['Not a valid string.'], "name" : ["Not a valid string."]})

        result, errors = ApiKeySchema().load({ "label" : "", "name" : "", "expiration" : 1, "username" : "", "password" : ""})
        self.assertEqual( errors, {'password': [' Data cannot be blank'], 'label': [' Data cannot be blank'], 'username': [' Data cannot be blank'], 'name': [' Data cannot be blank']})

class TestUserSchema(unittest.TestCase):
    def test_serializer(self):
        #with self.assertRaises(ValidationError) as context:
        #    ApiKeySchema().load({ "label" : 1234, "name" : "name"})
        #self.assertTrue("{'label': ['Not a valid string.']}" in str(context.exception))

        # CHECKING PHONE NUMBER
        data = {
            "username": "Lisa",
            "name"    : "Lisa",
            "msisdn"  : "0812123411111",
            "email"   : "lisa@bp.com",
            "password": "password",
        }
        result, errors = UserSchema().load(data)
        self.assertEqual( errors, {'msisdn': ['Invalid phone number']} )

        # CHECKING EMAIL
        data = {
            "username": "Lisa",
            "name"    : "Lisa",
            "msisdn"  : "081212341111",
            "email"   : "lisa!bp.com",
            "password": "password",
        }
        result, errors = UserSchema().load(data)
        self.assertEqual( errors, {'email': ['Invalid email']} )

        # CHECKING PASSWORD
        data = {
            "username": "Lisa",
            "name"    : "Lisa",
            "msisdn"  : "081212341111",
            "email"   : "lisa@bp.com",
            "password": "pass",
        }
        result, errors = UserSchema().load(data)
        self.assertEqual( errors, {'password': ['Invalid Password, Minimum 6 Character']} )

        # CHECKING ALL
        data = {
            "username": "Lisa",
            "name"    : "Lisa",
            "msisdn"  : "0812123411111",
            "email"   : "lisa!bp.com",
            "password": "pass",
        }
        result, errors = UserSchema().load(data)
        self.assertEqual( errors, {'email': ['Invalid email'], 'msisdn': ['Invalid phone number'], 'password': ['Invalid Password, Minimum 6 Character']})

class TestWalletSchema(unittest.TestCase):
    def test_serializer(self):
        #with self.assertRaises(ValidationError) as context:
        #    ApiKeySchema().load({ "label" : 1234, "name" : "name"})
        #self.assertTrue("{'label': ['Not a valid string.']}" in str(context.exception))

        # CHECKING PIN 
        data2 = {
            "name"   : "Lisa",
            "msisdn" : "081212341234",
            "email"  : "rose@bp.com",
            "pin"    : "12345",
        }
        result2, errors2 = WalletSchema().load(data2)
        self.assertEqual( errors2, {'pin': ['Invalid Pin, Minimum 4-6 digit']})

class TestTransactionSchema(unittest.TestCase):
    def test_serializer(self):
        data = {
            "source"      : 114620581380,
            "destination" : 118275863791,
            "pin"         : "123",
            "amount"      : 1,
            "notes"       : "Test",
        }
        result, errors = TransactionSchema().load(data)
        self.assertEqual(errors, {})

        data = {
            "source"      : 114620581380,
            "destination" : 118275863791,
            "pin"         : "123",
            "amount"      : -1,
            "notes"       : "Test",
        }
        result, errors = TransactionSchema().load(data)
        self.assertEqual(errors, {'amount': ['Invalid Amount, cannot be less than 0']})

        data = {
            "source"      : 114620581380,
            "destination" : 118275863791,
            "pin"         : "123",
            "amount"      : 0,
            "notes"       : "Test",
        }
        result, errors = TransactionSchema().load(data)
        self.assertEqual(errors, {'amount': ['Invalid Amount, cannot be less than 0']})

class TestCallbackSchema(unittest.TestCase):
    def test_serializer_success(self):
        data = {
            "trx_id"                   : 1230000001,
            "virtual_account"          : 9889909941749985,
            "customer_name"            : "Jennie",
            "trx_amount"               : 50000,
            "payment_amount"           : 100000,
            "cumulative_payment_amount": 100000,
            "payment_ntb"              : 233171,
            "datetime_payment"         : "2016-03-01 14:00:00",
        }
        errors = CallbackSchema().validate(data)
        self.assertEqual( errors, {})

    def test_serializer_failed(self):
        data = {
            "trx_id"                   : 1230000001,
            "virtual_account"          : 9889909941749985,
            "customer_name"            : "Jennie",
            "trx_amount"               : 1,
            "payment_amount"           : 1,
            "cumulative_payment_amount": 100000,
            "payment_ntb"              : 233171,
            "datetime_payment"         : "2016-03-01 14:00:00",
        }
        errors = CallbackSchema().validate(data)
        self.assertEqual( errors, {'payment_amount': ['Minimal deposit is 50000']} )

        data = {
            "trx_id"                   : 1230000001,
            "virtual_account"          : 9889909941749985,
            "customer_name"            : "Jennie",
            "trx_amount"               : 1,
            "payment_amount"           : 9999999999999999,
            "cumulative_payment_amount": 100000,
            "payment_ntb"              : 233171,
            "datetime_payment"         : "2016-03-01 14:00:00",
        }
        errors = CallbackSchema().validate(data)
        self.assertEqual( errors, {'payment_amount': ['Maximum deposit is 1000000000']} )

if __name__ == "__main__":
    unittest.main(verbosity=2)
