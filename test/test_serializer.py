import sys
import unittest

sys.path.append("../")
sys.path.append("../app")

from datetime import datetime, timedelta

from app            import create_app
from app.serializer import ApiKeySchema, WalletSchema, TransactionSchema
from app.config     import config

from marshmallow import ValidationError

now = datetime.utcnow()

class TestApiKeySchema(unittest.TestCase):
    def test_serializer(self):
        #with self.assertRaises(ValidationError) as context:
        #    ApiKeySchema().load({ "label" : 1234, "name" : "name"})
        #self.assertTrue("{'label': ['Not a valid string.']}" in str(context.exception))

        result, errors = ApiKeySchema().load({ "label" : "test", "name" : "name", "expiration" : 0})
        self.assertEqual( errors, {} )

        result, errors = ApiKeySchema().load({ "label" : 1234, "name" : "name" , "expiration" : 0})
        self.assertEqual( errors, {'label': ['Not a valid string.']})

        result, errors = ApiKeySchema().load({ "label" : 1234, "name" : 12345 , "expiration" : 0})
        self.assertEqual( errors, {'label': ['Not a valid string.'], "name" : ["Not a valid string."]})

        result, errors = ApiKeySchema().load({ "label" : "", "name" : "" , "expiration" : 0})
        self.assertEqual( errors, {'name': [' Data cannot be blank'], 'label': [' Data cannot be blank']})


class TestWalletSchema(unittest.TestCase):
    def test_serializer(self):
        #with self.assertRaises(ValidationError) as context:
        #    ApiKeySchema().load({ "label" : 1234, "name" : "name"})
        #self.assertTrue("{'label': ['Not a valid string.']}" in str(context.exception))

        # CHECKING PHONE NUMBER
        data = {
            "name"   : "Lisa",
            "msisdn" : "0812341234",
            "email"  : "lisa@bp.com",
            "pin"    : "123456",
        }
        result, errors = WalletSchema().load(data)
        self.assertEqual( errors, {'msisdn': ['Invalid phone number']} )

        # CHECKING PIN 
        data2 = {
            "name"   : "Lisa",
            "msisdn" : "081212341234",
            "email"  : "rose@bp.com",
            "pin"    : "12345",
        }
        result2, errors2 = WalletSchema().load(data2)
        self.assertEqual( errors2, {'pin': ['Invalid Pin, Minimum 4-6 digit']})

        # CHECKING EMAIL
        data3 = {
            "name"   : "Lisa",
            "msisdn" : "081212341234",
            "email"  : "lisabp.com",
            "pin"    : "123456",
        }
        result3, errors3 = WalletSchema().load(data3)
        self.assertEqual( errors3, {'email': ['Invalid email']})

        # ALL INVALID
        data4 = {
            "name"   : "Lisa",
            "msisdn" : "081341234",
            "email"  : "lisabp.com",
            "pin"    : "123",
        }
        result4, errors4 = WalletSchema().load(data4)

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

if __name__ == "__main__":
    unittest.main(verbosity=2)
