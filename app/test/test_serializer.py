import unittest

from datetime import datetime, timedelta

from app.test.base  import BaseTestCase
from app.api.serializer import UserSchema, WalletSchema, TransactionSchema, CallbackSchema
from app.api.config     import config

from marshmallow import ValidationError

now = datetime.utcnow()

class TestUserSchema(BaseTestCase):
    def test_serializer(self):
        pass

class TestWalletSchema(BaseTestCase):
    def test_serializer(self):
        # CHECKING PIN 
        data2 = {
            "name"   : "Lisa",
            "msisdn" : "081212341234",
            "email"  : "rose@bp.com",
            "pin"    : "12345",
        }
        result2, errors2 = WalletSchema().load(data2)
        self.assertEqual( errors2, {'pin': ['Invalid Pin, Minimum 4-6 digit']})

class TestTransactionSchema(BaseTestCase):
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

class TestCallbackSchema(BaseTestCase):
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
        self.assertEqual( errors, {'payment_amount': ['Maximum deposit is 100000000']} )

        data = {
            "trx_id"                   : 1230000001,
            "virtual_account"          : 9889909941749985,
            "customer_name"            : "Jennie",
            "trx_amount"               : 1,
            "payment_amount"           : -1,
            "cumulative_payment_amount": 100000,
            "payment_ntb"              : 233171,
            "datetime_payment"         : "2016-03-01 14:00:00",
        }
        errors = CallbackSchema().validate(data)
        self.assertEqual( errors, {'payment_amount': ['Minimal withdraw is 50000']} )

        data = {
            "trx_id"                   : 1230000001,
            "virtual_account"          : 9889909941749985,
            "customer_name"            : "Jennie",
            "trx_amount"               : 1,
            "payment_amount"           : -9999999999999999,
            "cumulative_payment_amount": 100000,
            "payment_ntb"              : 233171,
            "datetime_payment"         : "2016-03-01 14:00:00",
        }
        errors = CallbackSchema().validate(data)
        self.assertEqual( errors, {'payment_amount': ['Maximum withdraw is 100000000']} )

if __name__ == "__main__":
    unittest.main(verbosity=2)
