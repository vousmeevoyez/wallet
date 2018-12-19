from app.test.base      import BaseTestCase
from app.api.serializer import *
from app.api.config     import config

class TestUserSchema(BaseTestCase):

    def test_validate_username_failed_min_string(self):
        data = {
            "username"     : "Lisa",
            "name"         : "Lisa",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'username': ['Invalid username, minimum is 5 character']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_username_failed_max_string(self):
        data = {
            "username"     : "dsadasdasdhakshdklaskjhdjkhasdhjasklhsalhldsa",
            "name"         : "Lisa",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'username': ['Invalid username, max is 32 character']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_username_failed_alphanumeric_only(self):
        data = {
            "username"     : "*()**)",
            "name"         : "Lisa",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'username': ['Invalid username, only alphanumeric, . _ - allowed']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_username_success(self):
        data = {
            "username"     : "jennei",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
        }
        self.assertEqual(errors, expected_error)

    def test_validate_name_failed_min_string(self):
        data = {
            "username"     : "Jennie",
            "name"         : "a",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'name': ['Invalid name, minimum is 2 character']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_name_failed_max_string(self):
        data = {
            "username"     : "Jennie",
            "name"         : "jlajfljlsadjfljasjdf;ljas;ldfljasldfjajsdl;fja;lsjdfljad;lfj;lajsl;dfjas;dlj",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'name': ['Invalid name, max is 70 character']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_name_failed_alphanumeric_space_only(self):
        data = {
            "username"     : "Jennie",
            "name"         : "&^**&^&*^&*^*&^&*^*^",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'name': ['Invalid name, only alphabet allowed']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_name_success(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
        }
        self.assertEqual(errors, expected_error)

    def test_validate_phone_ext_success(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
        }
        self.assertEqual(errors, expected_error)

    def test_validate_phone_ext_failed_zero(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "000",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'phone_ext': ["phone ext can't be 0"]
        }
        self.assertEqual(errors, expected_error)

    def test_validate_phone_ext_failed_invalid(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "ABC",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'phone_ext': ['Invalid phone ext, only number allowed']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_phone_number_success(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
        }
        self.assertEqual(errors, expected_error)


    def test_validate_phone_number_failed_invalid(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "&*(&(&&(&(!&(&(!#",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'phone_number': ['Invalid phone number, only number allowed']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_phone_number_failed_zero(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "0000000000",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'phone_number': ["phone number can't be 0"]
        }
        self.assertEqual(errors, expected_error)

    def test_validate_email_success(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
        }
        self.assertEqual(errors, expected_error)

    def test_validate_email_failed_invalid(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa!bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'email': ['Invalid email']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_password_success(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
        }
        self.assertEqual(errors, expected_error)

    def test_validate_password_failed_min_password(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "pasrd",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'password': ['Invalid Password, Minimum 6 Character']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_pin_success(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
        }
        self.assertEqual(errors, expected_error)

    def test_validate_pin_failed_min_pin(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123",
            "role"         : "USER",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'pin': ['Invalid Pin, Minimum 6 digit']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_role_failed_invalid(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "&(*&*(&*(&*(&*(&",
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'role': ['Invalid Role, only alphabet allowed']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_role_failed_invalid_role(self):
        data = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219644314",
            "email"        : "lisa@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "MIMIN"
        }
        errors = UserSchema().validate(data)
        expected_error = {
            'role': ['Invalid Role']
        }
        self.assertEqual(errors, expected_error)
#end def

class TestWalletSchema(BaseTestCase):
    def test_serializer_success(self):
        # CHECKING PIN 
        data = {
            "name"   : "wendy",
            "msisdn" : "081212341234",
            "pin"    : "123456"
        }
        errors = WalletSchema().validate(data)
        self.assertEqual(errors, {})

    def test_validate_pin_failed_min_pin(self):
        data = {
            "name"   : "wendy",
            "msisdn" : "081212341234",
            "pin"    : "1234"
        }
        errors = WalletSchema().validate(data)
        expected_error = {
            'pin': ['Invalid Pin']
        }
        self.assertEqual(errors, expected_error)

class TestTransactionSchema(BaseTestCase):

    def test_validate_amount(self):
        data = {
            "wallet_id"        : 123456,
            "balance"          : 11,
            "amount"           : -1,
            "transaction_type" : 1,
            "notes"            : "test",
        }
        errors = TransactionSchema().validate(data)
        expected_error = {'amount': ['Invalid Amount, cannot be less than 0']}
        self.assertEqual(errors, expected_error)

class TestCallbackSchema(BaseTestCase):

    def test_validate_payment_amount_success(self):
        data = {
            "virtual_account"          : 9889909912490089,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : 50000,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {}
        self.assertEqual( errors, expected_error)

    def test_validate_payment_amount_failed_minimal_deposit(self):
        data = {
            "virtual_account"          : 9889909912490089,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : 1,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {
            'payment_amount': ['Minimal deposit is 50000']
        }
        self.assertEqual( errors, expected_error)

    def test_validate_payment_amount_failed_maximal_deposit(self):
        data = {
            "virtual_account"          : 9889909912490089,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : 99999999999999999999999,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {
            'payment_amount': ['Maximum deposit is 100000000']
        }
        self.assertEqual( errors, expected_error)

    def test_validate_payment_amount_failed_minimal_withdraw(self):
        data = {
            "virtual_account"          : 9889909912490089,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : -1,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {
            'payment_amount': ['Minimal withdraw is 50000']
        }
        self.assertEqual( errors, expected_error)

    def test_validate_payment_amount_failed_maximal_withdraw(self):
        data = {
            "virtual_account"          : 9889909912490089,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : -99999999999999999999999,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {
            'payment_amount': ['Maximum withdraw is 100000000']
        }
        self.assertEqual( errors, expected_error)

    def test_validate_va_number_success(self):
        data = {
            "virtual_account"          : 9889909912490089,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : 50000,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {}
        self.assertEqual( errors, expected_error)

    def test_validate_va_number_failed_not_16_digit(self):
        data = {
            "virtual_account"          : 988990991249008,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : 50000,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {
            'virtual_account': ['Invalid Virtual Account Number']
        }
        self.assertEqual( errors, expected_error)

    def test_validate_va_number_failed_first_3_digit_invalid(self):
        data = {
            "virtual_account"          : 123990991249008,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : 50000,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {
            'virtual_account': ['Invalid Virtual Account Number']
        }
        self.assertEqual( errors, expected_error)

    def test_validate_va_number_failed_invalid_client_id(self):
        data = {
            "virtual_account"          : 988111111249008,
            "customer_name"            : "jennie",
            "trx_id"                   : 872621408,
            "trx_amount"               : 1,
            "payment_amount"           : 50000,
            "cumulative_payment_amount": 1,
            "payment_ntb"              : 123456,
            "datetime_payment"         : "2018-11-27 15:58:47",
        }
        errors = CallbackSchema().validate(data)
        expected_error = {
            'virtual_account': ['Invalid Virtual Account Number']
        }
        self.assertEqual( errors, expected_error)

class TestBankAccountSchema(BaseTestCase):

    def test_validate_bank_account_name_success(self):
        data = {
            "account_no": "1111111110",
            "name"      : "irene red velvet",
            "label"     : "Irene Bank Account",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
        }
        self.assertEqual(errors, expected_error)

    def test_validate_bank_account_name_failed_min_string(self):
        data = {
            "account_no": "1111111110",
            "name"      : "a",
            "label"     : "Irene Bank Account",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            'name': ['Invalid name, minimum is 2 character']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_bank_account_name_failed_max_string(self):
        data = {
            "account_no": "1111111110",
            "name"      : "akdaslkdlajkdlasjdkljasjdkjakjdlsajldjlkajdjaljljdlajskljdlajskljdsa",
            "label"     : "Irene Bank Account",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            'name': ['Invalid name, max is 35 character']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_bank_account_name_failed_invalid(self):
        data = {
            "account_no": "1111111110",
            "name"      : "*!@()*)@*!)*@*!*@",
            "label"     : "Irene Bank Account",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            'name': ['Invalid name, only alphabet allowed']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_bank_account_no_failed(self):
        data = {
            "account_no": "0000000000",
            "name"      : "Irene",
            "label"     : "Irene Bank Account",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            'account_no': ["account no can't be 0"]
        }
        self.assertEqual(errors, expected_error)

        data = {
            "account_no": "abakdsalkdasjlk",
            "name"      : "Irene",
            "label"     : "Irene Bank Account",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            'account_no': ['Invalid account number, only number allowed']
        }
        self.assertEqual(errors, expected_error)

        data = {
            "account_no": "123456",
            "name"      : "Irene",
            "label"     : "Irene Bank Account",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            'account_no': ['Invalid account number, only number allowed']
        }
        self.assertEqual(errors, expected_error)

    def test_validate_bank_code_failed(self):
        data = {
            "account_no": "1234567891",
            "name"      : "Irene",
            "label"     : "Irene Bank Account",
            "bank_code" : "000"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            'bank_code': ["bank code can't be 0"]
        }
        self.assertEqual(errors, expected_error)

        data = {
            "account_no": "1234567891",
            "name"      : "Irene",
            "label"     : "Irene Bank Account",
            "bank_code" : "ads"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            'bank_code': ["Invalid bank code, only number allowed"]
        }
        self.assertEqual(errors, expected_error)

if __name__ == "__main__":
    unittest.main(verbosity=2)
