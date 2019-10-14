from datetime import datetime, timedelta
import pytest

from faker import Faker

from app import blueprint
from app.api import db
from app.api import celery
from app.api import create_app
from app.api.models import (
    User,
    Role,
    Bank,
    Wallet,
    VaType,
    VirtualAccount,
    BankAccount
)

from manage import init

from task.worker import celery

from tests.reusable.api_list import *

API_KEY = "8c574c41-3e01-4763-89af-fd370989da33"


@pytest.fixture(scope="module")
def setup_flask():
    flask_app = create_app("test")
    # register all known URL
    flask_app.register_blueprint(blueprint, url_prefix="/api/v1")

    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app

    ctx.pop()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    db.create_all()

    init()  # tirgger dump all mandatory data
    yield db

    db.session.remove()
    db.drop_all()


@pytest.fixture(scope="module")
def client(setup_flask, setup_db):
    """ fixture to initialize flask testing client """
    return setup_flask.test_client()


@pytest.fixture(scope="module")
def setup_role(setup_db):
    """ fixture for generate required role """
    role = Role(description="USER")
    db.session.add(role)
    db.session.commit()
    return role


@pytest.fixture(scope="module")
def setup_user_factory(setup_role):
    """ fixture for generate user using username only!"""
    def _setup_user_factory(username):
        user = User.query.filter_by(username=username).first()

        faker = Faker("en_US")
        original_name = faker.name()
        if user is None:
            user = User(
                username=username,
                name=original_name,
                email=faker.email(),
                phone_ext="62",
                phone_number=faker.msisdn()[0:10],
                role_id=setup_role.id,
            )
            user.set_password("password")

            db.session.add(user)
            db.session.commit()
        return user
    return _setup_user_factory


@pytest.fixture(scope="module")
def setup_user_only(setup_role):
    """ fixture for generate user only!"""
    user = User(
        username="dummyuser",
        name="somedummyuser",
        email="somedummyuser@test.com",
        phone_ext="62",
        phone_number="88308644314",
        role_id=setup_role.id,
    )
    user.set_password("password")

    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="module")
def setup_user_token(setup_user_only):
    """ fixture for generate user token """
    user = setup_user_only
    token = user.encode_token("ACCESS", user.id)
    return token.decode()

@pytest.fixture(scope="module")
def setup_user_token_factory(setup_user_factory):
    """ fixture for generate user token using username """
    def _setup_user_factory(username):
        user = setup_user_factory(username)
        token = user.encode_token("ACCESS", user.id)
        return token.decode()
    return _setup_user_factory


@pytest.fixture(scope="module")
def setup_admin_token(client):
    """ fixture for getting admin token """
    result = get_access_token(client, "MODANAADMIN", "password")
    response = result.get_json()
    return response["data"]["access_token"]


@pytest.fixture(scope="module")
def setup_user_wallet_va(client, setup_admin_token):
    """ fixture for creating user through api, wil trigger wallet and va
    creation also """
    faker = Faker("en_US")

    original_name = faker.name()
    username = (original_name.lower()).replace(" ", "_")

    payload = {
        "username": username,
        "name": original_name,
        "phone_ext": "62",
        "phone_number": faker.msisdn()[0:10],
        "email": faker.email(),
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    result = create_user(client, payload, setup_admin_token)
    response = result.get_json()["data"]

    # need to login!
    result = get_access_token(client, username, "password")
    user_access_token = result.get_json()["data"]["access_token"]
    # inject money
    wallet_id = response["wallet_id"]
    wallet = Wallet.query.filter_by(id=wallet_id).first()
    wallet.add_balance(100000)
    db.session.commit()

    return user_access_token, response["user_id"], response["wallet_id"]


@pytest.fixture(scope="module")
def setup_user_wallet_va_bank_acc(client, setup_user_wallet_va):

    access_token, user_id, wallet_id = setup_user_wallet_va

    # add account bank information
    params = {
        "account_no": "3333333333",
        "name": "Bpk KEN AROK",
        "label": "Irene Bank Account",
        "bank_code": "014",
    }
    result = create_user_bank_account(client, user_id, params, access_token)
    response = result.get_json()["data"]

    bank_account_id = response["bank_account_id"]
    return access_token, user_id, wallet_id, bank_account_id 


@pytest.fixture(scope="module")
def setup_user_wallet_va_without_balance(client, setup_admin_token):
    """ fixture for creating user through api, wil trigger wallet and va
    creation also """
    faker = Faker("en_US")

    original_name = faker.name()
    username = (original_name.lower()).replace(" ", "_")

    payload = {
        "username": username,
        "name": original_name,
        "phone_ext": "62",
        "phone_number": faker.msisdn()[0:10],
        "email": faker.email(),
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    result = create_user(client, payload, setup_admin_token)
    response = result.get_json()["data"]

    # need to login!
    result = get_access_token(client, username, "password")
    user_access_token = result.get_json()["data"]["access_token"]

    return user_access_token, response["user_id"], response["wallet_id"]


@pytest.fixture(scope="module")
def setup_wallet_info(client, setup_user_wallet_va):
    """ fixture for getting wallet and va information """
    user_access_token, user_id, wallet_id = setup_user_wallet_va

    result = get_wallet_info(client, wallet_id, user_access_token)
    response = result.get_json()["data"]
    return response


@pytest.fixture(scope="module")
def setup_wallet_with_balance(setup_db):
    """ fixture for creating wallet object only!"""
    wallet = Wallet()
    wallet.set_pin("123456")
    db.session.add(wallet)
    db.session.flush()
    wallet.add_balance(10000)
    db.session.commit()
    return wallet


@pytest.fixture(scope="module")
def setup_wallet_without_balance():
    """ fixture for creating wallet object only!"""
    wallet = Wallet()
    wallet.set_pin("123456")
    db.session.add(wallet)
    db.session.commit()
    return wallet


@pytest.fixture(scope="module")
def setup_bni_bank_account():
    """ fixture for creating bni bank account object !"""
    bank = Bank.query.filter_by(code="009").first()
    bank_account = BankAccount(account_no="123456", bank_id=bank.id)
    db.session.add(bank_account)
    db.session.commit()
    return bank_account


@pytest.fixture(scope="module")
def setup_bca_bank_account():
    """ fixture for creating bca bank account object !"""
    bank = Bank.query.filter_by(code="014").first()
    bank_account = BankAccount(account_no="123456", bank_id=bank.id)
    db.session.add(bank_account)
    db.session.commit()
    return bank_account


@pytest.fixture(scope="module")
def setup_bank():
    """ return bank object """
    bank = Bank.query.filter_by(code="009").first()
    return bank


@pytest.fixture(scope="module")
def setup_credit_va_type():
    """ return credit va type """
    credit_va_type = VaType.query.filter_by(key="CREDIT").first()
    return credit_va_type


@pytest.fixture(scope="module")
def setup_debit_va_type():
    """ return debit va type """
    debit_va_type = VaType.query.filter_by(key="DEBIT").first()
    return debit_va_type


@pytest.fixture(scope="module")
def setup_credit_va(setup_wallet_without_balance, setup_bank, setup_credit_va_type):
    """ fixture for creating credit va object only!"""
    credit_va = VirtualAccount(
        wallet_id=setup_wallet_without_balance.id,
        va_type_id=setup_credit_va_type.id,
        bank_id=setup_bank.id
    )
    va_number = credit_va.generate_va_number()
    va_trx_id = credit_va.generate_trx_id()

    db.session.add(credit_va)
    db.session.commit()

    return va_number, va_trx_id


@pytest.fixture(scope="module")
def setup_debit_va(setup_wallet_without_balance, setup_bank, setup_debit_va_type):
    """ fixture for creating debit va object only!"""
    debit_va = VirtualAccount(
        wallet_id=setup_wallet_without_balance.id,
        va_type_id=setup_debit_va_type.id,
        bank_id=setup_bank.id
    )
    va_number = debit_va.generate_va_number()
    va_trx_id = debit_va.generate_trx_id()

    db.session.add(debit_va)
    db.session.commit()

    return va_number, va_trx_id

@pytest.fixture(scope="module")
def setup_payment_plan_auto(client, setup_wallet_info):
    """ setup payment plan for auto mode (auto pay + auto debit)"""
    due_date = datetime.utcnow()
    plans = [{"amount": "1000", "type": "MAIN", "due_date": due_date.isoformat()}]

    params = {
        "destination": "123456",
        "method": "AUTO",
        "wallet_id": setup_wallet_info["id"],
        "plans": plans,
    }

    result = create_payment_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_payment_plan_auto_pay(client, setup_wallet_info):
    """ setup payment plan for auto pay"""
    due_date = datetime.utcnow()
    plans = [{"amount": "1000", "type": "MAIN", "due_date": due_date.isoformat()}]

    params = {
        "destination": "123456",
        "method": "AUTO_PAY",
        "wallet_id": setup_wallet_info["id"],
        "plans": plans,
    }

    result = create_payment_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_payment_plan_auto_debit(client, setup_wallet_info):
    """ setup payment plan for auto debit"""
    due_date = datetime.utcnow()
    plans = [{"amount": "1000", "type": "MAIN", "due_date": due_date.isoformat()}]

    params = {
        "destination": "123456",
        "method": "AUTO_DEBIT",
        "wallet_id": setup_wallet_info["id"],
        "plans": plans,
    }

    result = create_payment_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_additional_plan_for_auto(client, setup_payment_plan_auto):
    """ setup additional plan based on existing auto payment plan"""
    payment_plan_id = setup_payment_plan_auto["payment_plan_id"]

    # CREATE PLAN
    due_date = datetime.utcnow() + timedelta(minutes=1)
    params = {
        "payment_plan_id": payment_plan_id,
        "amount": "1000",
        "type": "ADDITIONAL",
        "due_date": due_date.isoformat(),
    }
    result = create_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_additional_plan_for_auto_debit(client, setup_payment_plan_auto_debit):
    """ setup additional plan based on existing auto debit payment plan"""
    payment_plan_id = setup_payment_plan_auto_debit["payment_plan_id"]

    # CREATE PLAN
    due_date = datetime.utcnow() + timedelta(minutes=1)
    params = {
        "payment_plan_id": payment_plan_id,
        "amount": "1000",
        "type": "ADDITIONAL",
        "due_date": due_date.isoformat(),
    }
    result = create_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_additional_plan_for_auto_pay(client, setup_payment_plan_auto_pay):
    """ setup additional plan based on existing auto pay payment plan"""
    payment_plan_id = setup_payment_plan_auto_pay["payment_plan_id"]

    # CREATE PLAN
    due_date = datetime.utcnow() + timedelta(minutes=1)
    params = {
        "payment_plan_id": payment_plan_id,
        "amount": "1000",
        "type": "ADDITIONAL",
        "due_date": due_date.isoformat(),
    }
    result = create_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response


@pytest.fixture(scope="module")
def setup_wallet_info(client, setup_user_wallet_va):
    """ fixture for getting wallet and va information """
    user_access_token, user_id, wallet_id = setup_user_wallet_va

    result = get_wallet_info(client, wallet_id, user_access_token)
    response = result.get_json()
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_wallet_info2(client, setup_user_wallet_va_without_balance):
    """ fixture for getting wallet and va information """
    user_access_token, user_id, wallet_id = \
    setup_user_wallet_va_without_balance

    result = get_wallet_info(client, wallet_id, user_access_token)
    response = result.get_json()
    response = result.get_json()["data"]
    return response


@pytest.fixture(scope="module")
def setup_wallet_with_balance(setup_db):
    """ fixture for creating wallet object only!"""
    wallet = Wallet()
    wallet.set_pin("123456")
    db.session.add(wallet)
    db.session.flush()
    wallet.add_balance(10000)
    db.session.commit()
    return wallet


@pytest.fixture(scope="module")
def setup_wallet_without_balance():
    """ fixture for creating wallet object only!"""
    wallet = Wallet()
    wallet.set_pin("123456")
    db.session.add(wallet)
    db.session.commit()
    return wallet


@pytest.fixture(scope="module")
def setup_bni_bank_account():
    """ fixture for creating bni bank account object !"""
    bank = Bank.query.filter_by(code="009").first()
    bank_account = BankAccount(account_no="123456", bank_id=bank.id)
    db.session.add(bank_account)
    db.session.commit()
    return bank_account


@pytest.fixture(scope="module")
def setup_bca_bank_account():
    """ fixture for creating bca bank account object !"""
    bank = Bank.query.filter_by(code="014").first()
    bank_account = BankAccount(account_no="123456", bank_id=bank.id)
    db.session.add(bank_account)
    db.session.commit()
    return bank_account


@pytest.fixture(scope="module")
def setup_bank():
    """ return bank object """
    bank = Bank.query.filter_by(code="009").first()
    return bank


@pytest.fixture(scope="module")
def setup_credit_va_type():
    """ return credit va type """
    credit_va_type = VaType.query.filter_by(key="CREDIT").first()
    return credit_va_type


@pytest.fixture(scope="module")
def setup_debit_va_type():
    """ return debit va type """
    debit_va_type = VaType.query.filter_by(key="DEBIT").first()
    return debit_va_type


@pytest.fixture(scope="module")
def setup_credit_va(setup_wallet_without_balance, setup_bank, setup_credit_va_type):
    """ fixture for creating credit va object only!"""
    credit_va = VirtualAccount(
        wallet_id=setup_wallet_without_balance.id,
        va_type_id=setup_credit_va_type.id,
        bank_id=setup_bank.id
    )
    va_number = credit_va.generate_va_number()
    va_trx_id = credit_va.generate_trx_id()

    db.session.add(credit_va)
    db.session.commit()

    return va_number, va_trx_id


@pytest.fixture(scope="module")
def setup_debit_va(setup_wallet_without_balance, setup_bank, setup_debit_va_type):
    """ fixture for creating debit va object only!"""
    debit_va = VirtualAccount(
        wallet_id=setup_wallet_without_balance.id,
        va_type_id=setup_debit_va_type.id,
        bank_id=setup_bank.id
    )
    va_number = debit_va.generate_va_number()
    va_trx_id = debit_va.generate_trx_id()

    db.session.add(debit_va)
    db.session.commit()

    return va_number, va_trx_id

@pytest.fixture(scope="module")
def setup_payment_plan_auto(client, setup_wallet_info):
    """ setup payment plan for auto mode (auto pay + auto debit)"""
    due_date = datetime.utcnow()
    plans = [{"amount": "1000", "type": "MAIN", "due_date": due_date.isoformat()}]

    params = {
        "destination": "123456",
        "method": "AUTO",
        "wallet_id": setup_wallet_info["id"],
        "plans": plans,
    }

    result = create_payment_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_payment_plan_auto_pay(client, setup_wallet_info):
    """ setup payment plan for auto pay"""
    due_date = datetime.utcnow()
    plans = [{"amount": "1000", "type": "MAIN", "due_date": due_date.isoformat()}]

    params = {
        "destination": "123456",
        "method": "AUTO_PAY",
        "wallet_id": setup_wallet_info["id"],
        "plans": plans,
    }

    result = create_payment_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_payment_plan_auto_debit(client, setup_wallet_info):
    """ setup payment plan for auto debit"""
    due_date = datetime.utcnow()
    plans = [{"amount": "1000", "type": "MAIN", "due_date": due_date.isoformat()}]

    params = {
        "destination": "123456",
        "method": "AUTO_DEBIT",
        "wallet_id": setup_wallet_info["id"],
        "plans": plans,
    }

    result = create_payment_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_additional_plan_for_auto(client, setup_payment_plan_auto):
    """ setup additional plan based on existing auto payment plan"""
    payment_plan_id = setup_payment_plan_auto["payment_plan_id"]

    # CREATE PLAN
    due_date = datetime.utcnow() + timedelta(minutes=1)
    params = {
        "payment_plan_id": payment_plan_id,
        "amount": "1000",
        "type": "ADDITIONAL",
        "due_date": due_date.isoformat(),
    }
    result = create_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_additional_plan_for_auto_debit(client, setup_payment_plan_auto_debit):
    """ setup additional plan based on existing auto debit payment plan"""
    payment_plan_id = setup_payment_plan_auto_debit["payment_plan_id"]

    # CREATE PLAN
    due_date = datetime.utcnow() + timedelta(minutes=1)
    params = {
        "payment_plan_id": payment_plan_id,
        "amount": "1000",
        "type": "ADDITIONAL",
        "due_date": due_date.isoformat(),
    }
    result = create_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response

@pytest.fixture(scope="module")
def setup_additional_plan_for_auto_pay(client, setup_payment_plan_auto_pay):
    """ setup additional plan based on existing auto pay payment plan"""
    payment_plan_id = setup_payment_plan_auto_pay["payment_plan_id"]

    # CREATE PLAN
    due_date = datetime.utcnow() + timedelta(minutes=1)
    params = {
        "payment_plan_id": payment_plan_id,
        "amount": "1000",
        "type": "ADDITIONAL",
        "due_date": due_date.isoformat(),
    }
    result = create_plan(client, params, API_KEY)
    response = result.get_json()["data"]
    return response