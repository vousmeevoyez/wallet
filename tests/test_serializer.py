"""
    Testing Serializer
"""
import pytest

from app.api.serializer import *
from app.api.models import *
from app.api import db
from app.config import config

from marshmallow.exceptions import ValidationError

""" 
    USER SERIALIZERS
"""

def test_validate_username_failed_min_string():
    data = {
        "username": "Lisa",
        "name": "Lisa",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"username": ["Invalid username, minimum is 5 character"]}
    assert errors == expected_error

def test_validate_username_failed_max_string():
    data = {
        "username": "dsadasdasdhakshdklaskjhdjkhasdhjasklhsalhldsa",
        "name": "Lisa",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"username": ["Invalid username, max is 32 character"]}
    assert errors == expected_error

def test_validate_username_failed_alphanumeric_only():
    data = {
        "username": "*()**)",
        "name": "Lisa",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {
        "username": ["Invalid username, only alphanumeric, . _ - allowed"]
    }
    assert errors == expected_error

def test_validate_username_success():
    data = {
        "username": "jennei",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_name_failed_min_string():
    data = {
        "username": "Jennie",
        "name": "a",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"name": ["Invalid name, minimum is 2 character"]}
    assert errors == expected_error

def test_validate_name_failed_max_string():
    data = {
        "username": "Jennie",
        "name": "jlajfljlsadjfljasjdf;ljas;ldfljasldfjajsdl;fja;lsjdfljad;lfj;lajsl;dfjas;dlj",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"name": ["Invalid name, max is 70 character"]}
    assert errors == expected_error

def test_validate_name_success():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_phone_ext_success():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_phone_ext_failed_zero():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "000",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"phone_ext": ["phone ext can't be 0"]}
    assert errors == expected_error

def test_validate_phone_ext_failed_invalid():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "ABC",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"phone_ext": ["Invalid phone ext, only number allowed"]}
    assert errors == expected_error

def test_validate_phone_number_success():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_phone_number_failed_invalid():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "&*(&(&&(&(!&(&(!#",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"phone_number": ["Invalid phone number, only number allowed"]}
    assert errors == expected_error

def test_validate_phone_number_failed_zero():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "0000000000",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"phone_number": ["phone number can't be 0"]}
    assert errors == expected_error

def test_validate_email_success():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_email_failed_invalid():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa!bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"email": ["Invalid email"]}
    assert errors == expected_error

def test_validate_password_success():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_password_failed_min_password():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "pasrd",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"password": ["Invalid Password, Minimum 6 Character"]}
    assert errors == expected_error

def test_validate_pin_success():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_pin_failed_min_pin():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123",
        "role": "USER",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {
        "pin": ["Invalid Pin, Only allowed 6 digit and must be integer"]
    }
    assert errors == expected_error

def test_validate_role_failed_invalid():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "&(*&*(&*(&*(&*(&",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"role": ["Invalid Role, only alphabet allowed"]}
    assert errors == expected_error

def test_validate_role_failed_invalid_role():
    data = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219644314",
        "email": "lisa@bp.com",
        "password": "password",
        "pin": "123456",
        "role": "MIMIN",
        "label": "PERSONAL",
    }
    errors = UserSchema().validate(data)
    expected_error = {"role": ["Invalid Role"]}
    assert errors == expected_error


def test_user_deserialize(setup_user_only):
    result = UserSchema().dump(setup_user_only).data
    assert result["msisdn"]
    assert result["status"]
    assert result["role"]

"""
    Wallet Serializer
"""

def test_validate_wallet():
    # CHECKING PIN
    data = {"label": "wendy", "msisdn": "081212341234", "pin": "123456"}
    errors = WalletSchema().validate(data)
    assert errors == {}

def test_validate_wallet_pin():
    data = {"name": "wendy", "msisdn": "081212341234", "pin": "1234"}
    errors = WalletSchema().validate(data)
    expected_error = {
        "label": ["Missing data for required field."],
        "pin": ["Invalid Pin, Only allowed 6 digit and must be integer"],
    }
    assert errors == expected_error


def test_validate_wallet_amount():
    data = {
        "wallet_id": "123456",
        "balance": 11,
        "amount": -1,
        "transaction_type": 1,
        "notes": "test",
    }
    errors = TransactionSchema().validate(data)
    expected_error = {"amount": ["Invalid Amount, cannot be less than 0"]}
    assert errors == expected_error


def test_wallet_deserialize(setup_wallet_with_balance, setup_wallet_without_balance):
    # start transaction here
    trx_amount = 10
    # first create debit payment
    debit_payment = Payment(
        source_account=setup_wallet_with_balance.id,
        to=setup_wallet_without_balance.id,
        amount=trx_amount,
        payment_type=False,
    )
    db.session.add(debit_payment)

    transaction_type = TransactionType.query.filter_by(key="TRANSFER_FEE").first()
    # create debit transaction
    debit_trx = Transaction(
        wallet_id=setup_wallet_with_balance.id,
        amount=trx_amount,
        payment_id=debit_payment.id,
        transaction_type_id=transaction_type.id,
        notes="something"
    )
    db.session.add(debit_trx)
    db.session.commit()

    result = TransactionSchema().dump(debit_trx).data
    assert result["balance"] == 0
    assert result["id"]
    assert result["transaction_type"]
    assert result["amount"]
    assert result["created_at"]
    assert result["payment_details"]
    assert result["payment_details"]["source"]
    assert result["payment_details"]["to"]
    assert result["payment_details"]["reference_number"] == None
    assert result["payment_details"]["payment_amount"]
    assert result["payment_details"]["payment_type"]
    assert result["payment_details"]["status"]
    assert result["wallet_id"]
    assert result["notes"]


def test_validate_callback_amount():
    data = {
        "virtual_account": 9889909912490089,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": 50000,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {}
    assert errors == expected_error


def test_validate_callback_min_deposit_amount():
    data = {
        "virtual_account": 9889909912490089,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": 1,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {"payment_amount": ["Minimal deposit is 50000"]}
    assert errors == expected_error


def test_validate_callback_max_deposit_amount():
    data = {
        "virtual_account": 9889909912490089,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": 99999999999999999999999,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {"payment_amount": ["Maximum deposit is 100000000"]}
    assert errors == expected_error


def test_validate_callback_min_withdraw_amount():
    data = {
        "virtual_account": 9889909912490089,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": -1,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {"payment_amount": ["Minimal withdraw is 50000"]}
    assert errors == expected_error


def test_validate_callback_max_withdraw_amount():
    data = {
        "virtual_account": 9889909912490089,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": -99999999999999999999999,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {"payment_amount": ["Maximum withdraw is 100000000"]}
    assert errors == expected_error

def test_validate_callback_va_number():
    data = {
        "virtual_account": 9889909912490089,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": 50000,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_callback_invalid_va_number():
    data = {
        "virtual_account": 988990991249008,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": 50000,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {"virtual_account": ["Invalid Virtual Account Number"]}
    assert errors == expected_error

    data = {
        "virtual_account": 123990991249008,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": 50000,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {"virtual_account": ["Invalid Virtual Account Number"]}
    assert errors == expected_error

    data = {
        "virtual_account": 988111111249008,
        "customer_name": "jennie",
        "trx_id": 872621408,
        "trx_amount": 1,
        "payment_amount": 50000,
        "cumulative_payment_amount": 1,
        "payment_ntb": 123456,
        "datetime_payment": "2018-11-27 15:58:47",
    }
    errors = CallbackSchema().validate(data)
    expected_error = {"virtual_account": ["Invalid Virtual Account Number"]}
    assert errors == expected_error

def test_validate_bank_account_name_success():
    data = {
        "account_no": "1111111110",
        "name": "irene red velvet",
        "label": "Irene Bank Account",
        "bank_id": "bank-id",
    }
    errors = BankAccountSchema().validate(data)
    expected_error = {}
    assert errors == expected_error

def test_validate_bank_account_name_failed_min_string():
    data = {
        "account_no": "1111111110",
        "name": "a",
        "label": "Irene Bank Account",
        "bank_id": "bank-id",
    }
    errors = BankAccountSchema().validate(data)
    expected_error = {"name": ["Invalid name, minimum is 2 character"]}
    assert errors == expected_error

def test_validate_bank_account_no_failed():
    data = {
        "account_no": "0000000000",
        "name": "Irene",
        "label": "Irene Bank Account",
        "bank_id": "bank-id",
    }
    errors = BankAccountSchema().validate(data)
    expected_error = {"account_no": ["account no can't be 0"]}
    assert errors == expected_error

    data = {
        "account_no": "abakdsalkdasjlk",
        "name": "Irene",
        "label": "Irene Bank Account",
        "bank_id": "bank-id",
    }
    errors = BankAccountSchema().validate(data)
    expected_error = {"account_no": ["Invalid account number, only number allowed"]}
    assert errors == expected_error

    data = {
        "account_no": "12345",
        "name": "Irene",
        "label": "Irene Bank Account",
        "bank_id": "bank-id",
    }
    errors = BankAccountSchema().validate(data)
    expected_error = {"account_no": ["Invalid account number, only number allowed"]}
    assert errors == expected_error

def test_validate_bank_account_label_min_string():
    data = {
        "account_no": "1111111110",
        "name": "irene red velvet",
        "label": "a",
        "bank_id": "bank-id",
    }
    errors = BankAccountSchema().validate(data)
    expected_error = {"label": ["Invalid label, minimum is 2 character"]}
    assert errors == expected_error

def test_validate_bank_account_label_max_string():
    data = {
        "account_no": "1111111110",
        "name": "irene red velvet",
        "label": "dsakldsadjalkjdljasjdkjasjdljasjdljalsjdlajsdjaljsdjdasjkjlkjlka",
        "bank_id": "bank-id",
    }
    errors = BankAccountSchema().validate(data)
    expected_error = {"label": ["Invalid label, max is 30 character"]}
    assert errors == expected_error

def test_validate_bank_account_label_invalid():
    data = {
        "account_no": "1111111110",
        "name": "irene red velvet",
        "label": "&@!*#&(@&(",
        "bank_id": "bank-id",
    }
    errors = BankAccountSchema().validate(data)
    expected_error = {"label": ["Invalid label, only alphabet allowed"]}
    assert errors == expected_error

def test_bank_id_to_name(setup_user_only, setup_bank):
    # create bank account here
    bank_account = BankAccount(name="Lisa", bank_id=setup_bank.id,
                               user_id=setup_user_only.id)
    db.session.add(bank_account)
    db.session.commit()

    result = BankAccountSchema().dump(bank_account).data
    assert result["id"]
    assert result["bank_name"]
    assert result["name"]
    assert result["label"] == None
    assert result["account_no"] == None

def test_validate_payment_schema_id():
    # no errors
    data = {
        "id": "some-payment-plan-id",
        "destination": "123456789",
        "wallet_id": "some-wallet-id",
    }
    errors = PaymentPlanSchema().validate(data)
    assert errors == {}

    # INVALID ID
    data = {
        "id": "#!@&#*(&@#(&#*",
        "destination": "123456789",
        "wallet_id": "some-wallet-id",
    }
    errors = PaymentPlanSchema().validate(data)
    expected_error = {"id": ["Invalid Identifier"]}
    assert errors == expected_error

    data = {"id": "abc", "destination": "123456789", "wallet_id": "some-wallet-id"}
    errors = PaymentPlanSchema().validate(data)
    expected_error = {"id": ["Invalid Identifier"]}
    assert errors == expected_error

    # register id first here
    payment_plan = PaymentPlan(id="some-payment-plan-id2")
    db.session.add(payment_plan)
    db.session.commit()

    # DUPLICATE ID
    data = {
        "id": "some-payment-plan-id2",
        "destination": "123456789",
        "wallet_id": "some-wallet-id",
    }
    with pytest.raises(ValidationError):
        data = PaymentPlanSchema(strict=True).load(data)

def test_validate_payment_schema_destination():
    # no errors
    data = {
        "id": "some-payment-plan-id",
        "destination": "123456789",
        "wallet_id": "some-wallet-id",
    }
    errors = PaymentPlanSchema().validate(data)
    assert errors == {}

    # INVALID destination
    data = {
        "id": "some-payment-plan-id",
        "destination": "00000000000000",
        "wallet_id": "some-wallet-id",
    }
    errors = PaymentPlanSchema().validate(data)
    expected_error = {"destination": ["destination can't be 0"]}
    assert errors == expected_error

    # INVALID destination
    data = {
        "id": "some-payment-plan-id",
        "destination": "asdklakskdasldjalksjldajs",
        "wallet_id": "some-wallet-id",
    }
    errors = PaymentPlanSchema().validate(data)
    expected_error = {
        "destination": ["Invalid destination account number, only number allowed"]
    }
    assert errors == expected_error

def test_validate_payment_schema_status():
    # no errors
    data = {
        "id": "some-payment-plan-id",
        "destination": "123456789",
        "wallet_id": "some-wallet-id",
        "status": "ACTIVE",
    }
    errors = PaymentPlanSchema().validate(data)
    assert errors == {}

    data = {
        "id": "some-payment-plan-id",
        "destination": "123456789",
        "wallet_id": "some-wallet-id",
        "status": "ACTIVE",
    }
    errors = PaymentPlanSchema().validate(data)
    assert errors == {}

    data = {
        "id": "some-payment-plan-id",
        "destination": "123456789",
        "wallet_id": "some-wallet-id",
        "status": "wowo",
    }
    errors = PaymentPlanSchema().validate(data)
    expected_error = {"status": ["Invalid status type"]}
    assert errors == expected_error

'''
def test_nested_plan():
    """ test serializing nested plan """
    plans = [
        {
            "amount": 10000,
            "type": "MAIN",
            "due_date": "2019-04-22T21:08:12",
        },
        {
            "amount": 10000,
            "type": "MAIN",
            "due_date": "2019-04-23T21:08:12",
        },
        {
            "amount": 10000,
            "type": "MAIN",
            "due_date": "2019-04-29T21:08:12",
        },
    ]

    data = {
        "method": "AUTO",
        "destination": "123456",
        "wallet_id": "some-wallet-id",
        "plans": plans,
    }
    payment_plan = PaymentPlanSchema(strict=True).load(data)
'''


def test_plan_id():
    data = {
        "id": "some-payment-plan-id",
        "amount": 10000,
        "type": "MAIN",
        "due_date": "2019-05-29T21:08:12",
    }
    errors = PlanSchema().validate(data)
    assert errors == {}

    data = {
        "id": "asdas",
        "amount": 10000,
        "type": "MAIN",
        "due_date": "2025-04-29T21:08:12",
    }
    errors = PlanSchema().validate(data)
    expected_error = {"id": ["Invalid Identifier"]}
    assert errors == expected_error

    data = {
        "id": "!@*(!@*(!*(@!(*@",
        "amount": 10000,
        "type": "MAIN",
        "due_date": "2019-06-29T21:08:12",
    }
    errors = PlanSchema().validate(data)
    expected_error = {"id": ["Invalid Identifier"]}
    assert errors == expected_error

    # duplicate
    plan = Plan(id="some-plan-id")
    db.session.add(plan)
    db.session.commit()

    data = {
        "id": "some-plan-id",
        "amount": 10000,
        "type": "MAIN",
        "due_date": "2019-07-30T21:08:12",
    }
    with pytest.raises(ValidationError):
        result = PlanSchema(strict=True).load(data)

def test_plan_amount():
    data = {
        "id": "some-payment-plan-id",
        "amount": -10000,
        "type": "MAIN",
        "due_date": "2019-08-29T21:08:12",
    }
    errors = PlanSchema().validate(data)
    expected_error = {"amount": ["Invalid Amount, cannot be less than 0"]}
    assert errors == expected_error

def test_plan_type():
    data = {
        "id": "some-payment-plan-id",
        "amount": 10000,
        "type": "SECONDARY",
        "due_date": "2022-01-30T21:08:12",
    }
    errors = PlanSchema().validate(data)
    expected_error = {"type": ["Invalid plan type"]}
    assert errors == expected_error

def test_plan_due_date():
    data = {
        "id": "some-payment-plan-id",
        "amount": 10000,
        "type": "MAIN",
        "due_date": "2019!06-11",
    }
    errors = PlanSchema().validate(data)
    expected_error = {"due_date": ["Invalid isoformat string: '2019!06-11'"]}
    assert errors == expected_error

    data = {
        "id": "some-payment-plan-id",
        "amount": 10000,
        "type": "MAIN",
        "due_date": "2019-02-30",
    }
    errors = PlanSchema().validate(data)
    expected_error = {"due_date": ["day is out of range for month"]}
    assert errors == expected_error
