from app.test.base      import BaseTestCase
from app.api.serializer import *
from app.api.models     import *
from app.config     import config

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

    def test_deserialize(self):
        role = Role(
            description="USER",
        )
        db.session.add(role)
        db.session.commit()

        # create dummy user
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            phone_ext='62',
            phone_number='81219644314',
            role_id=role.id,
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        result = UserSchema().dump(user).data
        self.assertEqual(result["msisdn"], "6281219644314")
        self.assertEqual(result["status"], "ACTIVE")
        self.assertEqual(result["role"], "USER")
#end def

class TestWalletSchema(BaseTestCase):
    def test_serializer_success(self):
        # CHECKING PIN 
        data = {
            "label"  : "wendy",
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
        expected_error = {'label': ['Missing data for required field.'],
                          'pin': ['Invalid Pin']}
        self.assertEqual(errors, expected_error)

class TestTransactionSchema(BaseTestCase):

    def test_validate_amount(self):
        data = {
            "wallet_id"        : "123456",
            "balance"          : 11,
            "amount"           : -1,
            "transaction_type" : 1,
            "notes"            : "test",
        }
        errors = TransactionSchema().validate(data)
        expected_error = {'amount': ['Invalid Amount, cannot be less than 0']}
        self.assertEqual(errors, expected_error)

    def test_deserialize(self):
         # create 2 dummy wallet here
        wallet = Wallet(
        )
        wallet2 = Wallet(
        )

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.flush()

        # add some balance here for test case
        user = Wallet.query.get(1)
        user.add_balance(1000)
        db.session.flush()

        self.assertEqual(user.check_balance(), 1000)

        user2 = Wallet.query.get(2)
        user2.add_balance(1000)
        db.session.flush()

        self.assertEqual(user2.check_balance(), 1000)

        #start transaction here
        trx_amount = 10
        # first create debit payment
        debit_payment = Payment(
            source_account=wallet.id,
            to=wallet2.id,
            amount=trx_amount,
            payment_type=False,
        )
        db.session.add(debit_payment)

        #create debit transaction
        debit_trx = Transaction(
            wallet_id=wallet.id,
            amount=trx_amount,
            payment_id=debit_payment.id
        )
        debit_trx.generate_trx_id()
        db.session.add(debit_trx)
        # deduct balance

        db.session.commit()

        result = TransactionSchema().dump(debit_trx).data
        self.assertEqual(result["transaction_type"], "RECEIVE_TRANSFER")

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

    def test_validate_bank_account_label_min_string(self):
        data = {
            "account_no": "1111111110",
            "name"      : "irene red velvet",
            "label"     : "a",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            "label" : [ "Invalid label, minimum is 2 character" ]
        }
        self.assertEqual(errors, expected_error)

    def test_validate_bank_account_label_max_string(self):
        data = {
            "account_no": "1111111110",
            "name"      : "irene red velvet",
            "label"     : "dsakldsadjalkjdljasjdkjasjdljasjdljalsjdlajsdjaljsdjdasjkjlkjlka",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            "label" : [ "Invalid label, max is 30 character" ]
        }
        self.assertEqual(errors, expected_error)

    def test_validate_bank_account_label_invalid(self):
        data = {
            "account_no": "1111111110",
            "name"      : "irene red velvet",
            "label"     : "&@!*#&(@&(",
            "bank_code" : "009"
        }
        errors = BankAccountSchema().validate(data)
        expected_error = {
            "label" : [ "Invalid label, only alphabet allowed" ]
        }
        self.assertEqual(errors, expected_error)

    def test_bank_id_to_name(self):
        role = Role(
            description="USER",
        )
        db.session.add(role)
        db.session.commit()

        # create dummy user
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            phone_ext='62',
            phone_number='81219644314',
            role_id=role.id,
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # create bank here
        bank_name = "Bank BNI"
        bni=Bank(
            key="BNI",
            name=bank_name,
            code="99",
        )
        db.session.add(bni)
        db.session.commit()

        # create bank account here
        bank_account = BankAccount(
            name="Lisa",
            bank_id=bni.id,
            user_id=user.id
        )
        db.session.add(bank_account)
        db.session.commit()

        result = BankAccountSchema().dump(bank_account).data
        self.assertEqual(result["bank_name"],bank_name)

if __name__ == "__main__":
    unittest.main(verbosity=2)
