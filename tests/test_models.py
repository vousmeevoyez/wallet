"""
    Test Models
    ___________
"""
import pytest
from datetime import date, datetime, timedelta
from dateutil import relativedelta

from sqlalchemy.sql import func

from app.api import db
from app.api.models import *
from app.config import config

from app.api.auth.exceptions import *

from sqlalchemy.exc import IntegrityError, InvalidRequestError


def test_quota(setup_wallet_with_balance, setup_transaction):
    quota = Quota(
        no_of_transactions=3, reward_amount=3000, wallet_id=setup_wallet_with_balance.id
    )
    db.session.add(quota)
    db.session.commit()

    quota_usage = QuotaUsage(quota_id=quota.id, transaction_id=setup_transaction.id)
    db.session.add(quota_usage)
    db.session.commit()


def test_transaction_link():
    """ test self ref credit trx with debit trx"""
    # create 2 dummy wallet here
    wallet = Wallet()
    wallet2 = Wallet()

    db.session.add(wallet)
    db.session.add(wallet2)
    db.session.flush()

    wallet.add_balance(1000)
    db.session.flush()

    assert wallet.balance == 1000

    wallet2.add_balance(1000)
    db.session.flush()

    assert wallet2.balance == 1000

    # start transaction here
    amount = -10
    # first create debit payment
    debit_payment = Payment(
        source_account=wallet.id, to=wallet2.id, amount=amount, payment_type=False
    )
    db.session.add(debit_payment)

    # create debit transaction
    debit_trx = Transaction(wallet_id=wallet.id, amount=amount)
    db.session.add(debit_trx)
    # deduct balance
    wallet.add_balance(amount)

    db.session.flush()

    # start another transaction here
    amount = 10
    # second create credit payment
    credit_payment = Payment(source_account=wallet.id, to=wallet2.id, amount=amount)
    db.session.add(credit_payment)

    # create debit transaction
    credit_trx = Transaction(wallet_id=wallet2.id, amount=amount)
    db.session.add(credit_trx)
    # deduct user balance here
    wallet2.add_balance(amount)

    db.session.flush()

    # link transaction
    debit_trx.parent_id = credit_trx.id
    credit_trx.parent_id = debit_trx.id
    db.session.commit()

    # make sure each account have correct balance after each transaction
    assert wallet.balance == 990
    assert len(wallet.transactions) == 1

    assert wallet2.balance == 1010
    assert len(wallet2.transactions) == 1

def test_transaction_link2():
    """ test self ref debit trx with fee trx and cashback trx """
    # create 2 dummy wallet here
    wallet = Wallet()

    db.session.add(wallet)
    db.session.flush()

    wallet.add_balance(1000)
    db.session.flush()

    assert wallet.balance == 1000

    # start transaction here
    amount = -10
    # first create debit payment
    debit_payment = Payment(
        source_account=wallet.id,
        to="some-bank-acc-id",
        amount=amount,
        payment_type=False
    )
    db.session.add(debit_payment)

    # create debit transaction
    debit_trx = Transaction(
        wallet_id=wallet.id,
        amount=amount
    )
    db.session.add(debit_trx)
    # deduct balance
    wallet.add_balance(amount)

    db.session.flush()

    # create transfer fee payment
    amount = -1
    fee_payment = Payment(
        source_account=wallet.id,
        to="some-bank-acc-id",
        amount=amount
    )
    db.session.add(fee_payment)
    # create transfer fee transaction
    fee_trx = Transaction(
        wallet_id=wallet.id,
        amount=amount
    )
    db.session.add(fee_trx)
    # deduct user balance here
    wallet.add_balance(amount)

    db.session.flush()

    # create cashback transfer fee payment
    amount = 1
    reward_payment = Payment(
        source_account="N/A",
        to=wallet.id,
        amount=amount
    )
    db.session.add(reward_payment)
    # create transfer fee transaction
    reward_trx = Transaction(
        wallet_id=wallet.id,
        amount=amount
    )
    db.session.add(reward_trx)
    # deduct user balance here
    wallet.add_balance(amount)

    db.session.flush()

    # link transaction
    # debit -> fee -> reward
    #debit_trx.children = fee_trx
    fee_trx.parent_id = debit_trx.id
    reward_trx.parent_id = fee_trx.id
    db.session.commit()

    # make sure each account have correct balance after each transaction
    assert wallet.balance == 990
    assert len(wallet.transactions) == 3

'''
def test_user_role_relation(setup_user_only):
    """ test relationship between User & Role"""
    # create user role first
    # get user by their role
    role = Role.query.filter_by(description="USER").first()
    assert len(role.user) > 0


def test_user_wallet_relation(setup_user_only, setup_wallet_with_balance):
    """ test relationship between User & Wallet """
    # create dummy user
    user = setup_user_only
    wallet = setup_wallet_with_balance

    wallet.user = user
    db.session.commit()

    # check how many wallet user have
    assert len(user.wallets) == 1


def test_user_password(setup_user_only):
    """ test generate password"""
    # check password here
    assert setup_user_only.check_password("password")
    assert setup_user_only.check_password("test") == False


def test_user_encode_token(setup_user_only):
    """ test encode a token"""
    token = setup_user_only.encode_token("ACCESS", setup_user_only.id)
    assert isinstance(token, bytes)

def test_user_decode_token(setup_user_only):
    """ test decode token"""
    token = setup_user_only.encode_token("ACCESS", setup_user_only.id)
    assert isinstance(token, bytes)

    token = token.decode("utf-8")

    # make sure the decoded token contain following information
    assert setup_user_only.decode_token(token)["type"] == "ACCESS"

    with pytest.raises(EmptyPayloadError):
        setup_user_only.decode_token(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6Im5vbmUifQ.e30.kligm-MjaliTD584hBs6v52XSZcixYU9BlmAAwmjOB0"
        )


def test_wallet_check_balance():
    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    # check balance
    assert wallet.balance == 0


def test_wallet_add_balance():
    # create dummy wallet
    wallet = Wallet()

    db.session.add(wallet)
    db.session.commit()

    # add balance here
    wallet.add_balance(1000)
    wallet.add_balance(1000)
    wallet.add_balance(1000)
    wallet.add_balance(1000)
    wallet.add_balance(1000)

    assert wallet.balance == 5000

def test_wallet_check_lock():
    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    lock_status = wallet.is_unlocked()

    # check wallet status
    assert lock_status

def test_wallet_lock():
    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    wallet.lock()

    # check lock here
    lock_status = wallet.is_unlocked()
    assert lock_status is False

def test_wallet_unlock():
    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    wallet.lock()

    # unlock here
    wallet.unlock()
    lock_status = wallet.is_unlocked()

    # make sure the wallet is unlocked
    assert lock_status

def test_wallet_pin():
    # create dummy wallet here
    wallet = Wallet()
    # set pin
    wallet.set_pin("123456")

    # check pin
    result = wallet.check_pin("123456")
    assert result == "CORRECT"

    # incorrect 3 times
    result = wallet.check_pin("121456")
    assert result == "INCORRECT"

    result = wallet.check_pin("121456")
    assert result == "INCORRECT"

    result = wallet.check_pin("121456")
    assert result == "INCORRECT"

    result = wallet.check_pin("121456")
    assert result == "MAX_ATTEMPT"

    result = wallet.check_pin("121456")
    assert result == "LOCKED"

    result = wallet.check_pin("121456")
    assert result == "LOCKED"

    result = wallet.check_pin("121456")
    assert result == "LOCKED"

def test_wallet_va_relationship():
    # create dummy wallet here
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    # create bank here
    bni = Bank(key="BNI", code="009")
    db.session.add(bni)
    db.session.commit()

    # create virtual_account_type here
    # credit
    va_credit = VaType(key="CREDIT")

    # debit
    va_debit = VaType(key="DEBIT")
    db.session.add(va_debit)
    db.session.add(va_credit)
    db.session.commit()

    # create virtual account credit
    va = VirtualAccount(
        amount="100",
        name="Lisa",
        wallet_id=wallet.id,
        bank_id=bni.id,
        va_type_id=va_credit.id,
    )
    va_id = va.generate_va_number()
    trx_id = va.generate_trx_id()
    db.session.add(va)
    db.session.commit()

    # create virtual account debit
    va = VirtualAccount(
        amount="101",
        name="Lisa",
        wallet_id=wallet.id,
        bank_id=bni.id,
        va_type_id=va_debit.id,
    )
    va_id = va.generate_va_number()
    trx_id = va.generate_trx_id()

    db.session.add(va)
    db.session.commit()

    # make sure 2 virtual account is associated with wallet
    assert len(wallet.virtual_accounts) == 2

    # make sure each virtual acount type is associate with virtual account
    assert len(va_credit.virtual_account) == 1
    assert len(va_debit.virtual_account) == 1

    # make sure each bank is associated with virtual_account
    assert len(bni.virtual_account) == 2

def test_wallet_is_owned():
    # create dummy user here
    user = User(
        username="lisabp",
        name="lisa",
        email="lisa@bp.com",
        phone_ext="62",
        phone_number="81219644314",
    )
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # create user wallet here
    wallet = Wallet(user_id=user.id)
    db.session.add(wallet)
    db.session.commit()

    result = Wallet.is_owned(user.id, wallet.id)
    assert result

def test_wallet_total_balance():

    wallet = Wallet(balance=1000)
    wallet2 = Wallet(balance=1000)
    db.session.add(wallet)
    db.session.add(wallet2)
    db.session.commit()

    assert Wallet.total_balance() == 2000


def test_va_create():
    # create virtual_account_type here
    # credit
    va_credit = VaType(key="CREDIT")

    db.session.add(va_credit)
    db.session.commit()

    # create bank here
    bank = Bank(key="BNI", name="Bank BNI", code="009")
    db.session.add(bank)
    db.session.commit()

    # create virtual account credit
    va = VirtualAccount(
        amount="100", name="Lisa", va_type_id=va_credit.id, bank_id=bank.id
    )
    va_id = va.generate_va_number()
    trx_id = va.generate_trx_id()
    datetime_expired = va.get_datetime_expired("BNI", "CREDIT")
    db.session.add(va)
    db.session.commit()

    log = VaLog(virtual_account_id=va.id, balance=1000)
    db.session.add(log)
    db.session.commit()

    logs = VaLog.query.all()
    assert len(logs) == 1

def test_va_generate_number():
    # create virtual_account_type here
    # credit
    va_credit = VaType(key="CREDIT")

    # debit
    va_debit = VaType(key="DEBIT")
    db.session.add(va_debit)
    db.session.add(va_credit)
    db.session.commit()

    # create bank here
    bank = Bank(key="BNI", name="Bank BNI", code="009")
    db.session.add(bank)
    db.session.commit()

    # create virtual account credit
    va = VirtualAccount(
        amount="100", name="Lisa", va_type_id=va_credit.id, bank_id=bank.id
    )
    va_id = va.generate_va_number()
    trx_id = va.generate_trx_id()
    datetime_expired = va.get_datetime_expired("BNI", "CREDIT")
    db.session.add(va)
    db.session.commit()

    va_number = va.generate_va_number()
    assert len(va_number) == 16


def test_debit_transaction():
    # create 2 dummy wallet here
    wallet = Wallet()
    wallet2 = Wallet()

    db.session.add(wallet)
    db.session.add(wallet2)
    db.session.flush()

    wallet.add_balance(1000)
    db.session.flush()

    assert wallet.balance == 1000

    wallet2.add_balance(1000)
    db.session.flush()

    assert wallet2.balance == 1000

    # start transaction here
    amount = -10
    # first create debit payment
    debit_payment = Payment(
        source_account=wallet.id, to=wallet2.id, amount=amount, payment_type=False
    )
    db.session.add(debit_payment)

    # create debit transaction
    debit_trx = Transaction(wallet_id=wallet.id, amount=amount)
    db.session.add(debit_trx)
    # deduct balance
    wallet.add_balance(amount)

    db.session.flush()

    # start another transaction here
    amount = 10
    # second create credit payment
    credit_payment = Payment(source_account=wallet.id, to=wallet2.id, amount=amount)
    db.session.add(credit_payment)

    # create debit transaction
    credit_trx = Transaction(wallet_id=wallet2.id, amount=amount)
    db.session.add(credit_trx)
    # deduct user balance here
    wallet2.add_balance(amount)

    db.session.flush()

    # make sure each account have correct balance after each transaction
    assert wallet.balance == 990
    assert len(wallet.transactions) == 1

    assert wallet2.balance == 1010
    assert len(wallet2.transactions) == 1

def test_transaction_link():
    # create 2 dummy wallet here
    wallet = Wallet()
    wallet2 = Wallet()

    db.session.add(wallet)
    db.session.add(wallet2)
    db.session.flush()

    wallet.add_balance(1000)
    db.session.flush()

    assert wallet.balance == 1000

    wallet2.add_balance(1000)
    db.session.flush()

    assert wallet2.balance == 1000

    # start transaction here
    amount = -10
    # first create debit payment
    debit_payment = Payment(
        source_account=wallet.id, to=wallet2.id, amount=amount, payment_type=False
    )
    db.session.add(debit_payment)

    # create debit transaction
    debit_trx = Transaction(wallet_id=wallet.id, amount=amount)
    db.session.add(debit_trx)
    # deduct balance
    wallet.add_balance(amount)

    db.session.flush()

    # start another transaction here
    amount = 10
    # second create credit payment
    credit_payment = Payment(source_account=wallet.id, to=wallet2.id, amount=amount)
    db.session.add(credit_payment)

    # create debit transaction
    credit_trx = Transaction(wallet_id=wallet2.id, amount=amount)
    db.session.add(credit_trx)
    # deduct user balance here
    wallet2.add_balance(amount)

    db.session.flush()

    # link transaction
    debit_trx.transaction_link_id = credit_trx.id
    credit_trx.transaction_link_id = debit_trx.id
    db.session.commit()

    # make sure each account have correct balance after each transaction
    assert wallet.balance == 990
    assert len(wallet.transactions) == 1

    assert wallet2.balance == 1010
    assert len(wallet2.transactions) == 1


def test_set_otp_code():
    # create wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    # create forgot pin record
    forgot_pin = ForgotPin(wallet_id=wallet.id)
    forgot_pin.set_otp_code("123456")
    db.session.add(forgot_pin)
    db.session.commit()

    count = ForgotPin.query.all().count()
    assert count == 1

def test_check_otp_code():
    # create wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    # create forgot pin record
    forgot_pin = ForgotPin(wallet_id=wallet.id)
    forgot_pin.set_otp_code("123456")
    db.session.add(forgot_pin)
    db.session.commit()

    result = forgot_pin.check_otp_code("123456")
    assert result

def test_check_valid_otp_log():
    # create wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    # create forgot pin record
    valid_until = datetime.now() + timedelta(minutes=5)

    forgot_pin = ForgotPin(wallet_id=wallet.id, valid_until=valid_until)
    forgot_pin.set_otp_code("123456")
    db.session.add(forgot_pin)
    db.session.commit()

    # check record and make sure there's a pending otp record
    result = ForgotPin.query.filter(
        ForgotPin.wallet_id == wallet.id,
        ForgotPin.status == False,
        ForgotPin.valid_until > datetime.now(),
    ).count()
    assert result == 1

def test_check_invalid_otp_log():
    # create wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    # create forgot pin record
    valid_until = datetime.now() - timedelta(minutes=5)

    forgot_pin = ForgotPin(wallet_id=wallet.id, valid_until=valid_until)
    forgot_pin.set_otp_code("123456")
    db.session.add(forgot_pin)
    db.session.commit()

    # check record and make sure there's a pending otp record
    result = ForgotPin.query.filter(
        ForgotPin.wallet_id == wallet.id,
        ForgotPin.status == False,
        ForgotPin.valid_until > datetime.now(),
    ).count()
    assert result == 0


def test_withdraw_wallet():
    # create wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    # create forgot pin record
    valid_until = datetime.now() - timedelta(minutes=5)

    withdraw = Withdraw(wallet_id=wallet.id, valid_until=valid_until)
    db.session.add(withdraw)
    db.session.commit()

    # check record and make sure there's a pending otp record
    result = Withdraw.query.filter(
        Withdraw.wallet_id == wallet.id, Withdraw.valid_until > datetime.now()
    ).count()
    assert result == 0


def test_relation_bank_account():
    role = Role(description="USER")
    db.session.add(role)
    db.session.commit()

    # create dummy user
    user = User(
        username="lisabp",
        name="lisa",
        email="lisa@bp.com",
        phone_ext="62",
        phone_number="81219644314",
        role_id=role.id,
    )
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # create bank here
    bni = Bank(key="BNI", name="Bank BNI", code="99")
    db.session.add(bni)
    db.session.commit()

    # create bank account here
    bank_account = BankAccount(name="Lisa", bank_id=bni.id, user_id=user.id)
    db.session.add(bank_account)
    db.session.commit()

    # create another bank here
    bca = Bank(key="BCA", name="Bank BCA", code="100")
    db.session.add(bca)
    db.session.commit()

    # create bank account here
    bank_account = BankAccount(name="Ririn", bank_id=bca.id, user_id=user.id)
    db.session.add(bank_account)
    db.session.commit()

    # make sure user is associated to bank account
    assert len(user.bank_accounts) == 2


def test_payment_channel():
    # create bank here
    bni = Bank(key="BNI", name="Bank BNI", code="99")
    db.session.add(bni)
    db.session.commit()

    # create payment channel
    payment_channel1 = PaymentChannel(
        name="BNI Virtual Account",
        key="BNI_VA",
        channel_type="VIRTUAL_ACCOUNT",
        bank_id=bni.id,
    )
    db.session.add(payment_channel1)

    # create payment channel
    payment_channel2 = PaymentChannel(
        name="BNI Transfer",
        key="BNI_TRANSFER",
        channel_type="TRANSFER",
        bank_id=bni.id,
    )
    db.session.add(payment_channel2)
    db.session.commit()

    assert len(bni.payment_channels) == 2

def test_payment_model():
    # create bank here
    bni = Bank(key="BNI", name="Bank BNI", code="99")
    db.session.add(bni)
    db.session.commit()

    # create payment channel
    payment_channel1 = PaymentChannel(
        name="BNI Virtual Account",
        key="BNI_VA",
        channel_type="VIRTUAL_ACCOUNT",
        bank_id=bni.id,
    )
    db.session.add(payment_channel1)

    # create payment channel
    payment_channel2 = PaymentChannel(
        name="BNI Transfer",
        key="BNI_TRANSFER",
        channel_type="TRANSFER",
        bank_id=bni.id,
    )
    db.session.add(payment_channel2)
    db.session.flush()

    # payment
    payment = Payment(
        source_account="123456",
        ref_number="111111",
        amount=1,
        to="123",
        channel_id=payment_channel1.id,
    )
    db.session.add(payment)

    # payment 2
    payment2 = Payment(
        source_account="133456",
        ref_number="111112",
        amount=2,
        channel_id=payment_channel2.id,
        to="123",
    )
    db.session.add(payment2)
    db.session.commit()

    payments = (
        Payment.query.join(PaymentChannel)
        .join(Bank)
        .filter(PaymentChannel.bank_id == bni.id)
        .all()
    )
    assert len(payments) == 2

def test_incorrect_pin():
    """ 
        simulate incorrect pin where person enter incorrect pin 3 times
    """
    # create wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    # first check and make sure there's no incorrect pin record
    result = IncorrectPin.query.filter(
        IncorrectPin.wallet_id == wallet.id,
        IncorrectPin.valid_until > datetime.now(),
    ).first()
    assert result ==  None

    # user enter incorrect pin create a incorrect pin record here
    # this record valid for next 60 minutes
    valid_until = datetime.now() + timedelta(minutes=60)
    incorrect_attempt = IncorrectPin(wallet_id=wallet.id, valid_until=valid_until)
    db.session.add(incorrect_attempt)
    db.session.commit()

    # second check and make sure there's incorrect pin record
    incorrect_pin = IncorrectPin.query.filter(
        IncorrectPin.wallet_id == wallet.id,
        IncorrectPin.valid_until > datetime.now(),
    ).first()
    assert incorrect_pin.attempt == 1

    # update incorrect pin attempt
    incorrect_pin.attempt += 1
    db.session.commit()

    # check and make sure there's incorrect pin record
    incorrect_pin = IncorrectPin.query.filter(
        IncorrectPin.wallet_id == wallet.id,
        IncorrectPin.valid_until > datetime.now(),
    ).first()
    assert incorrect_pin.attempt == 2

    # update incorrect pin attempt
    incorrect_pin.attempt += 1
    db.session.commit()

    # check and make sure there's incorrect pin record
    result = IncorrectPin.query.filter(IncorrectPin.wallet_id == wallet.id).first()

def test_payment_plan_january_fee():
    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()
    # add balance here
    wallet.add_balance(1000)

    # create payment plan
    payment_plan = PaymentPlan(
        destination="some-bank-account-number", wallet_id=wallet.id
    )
    db.session.add(payment_plan)
    db.session.commit()

    # create plan
    due_date = datetime(2019, 1, 25)
    january_plan = Plan(
        payment_plan_id=payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(january_plan)

    # create plan
    due_date = datetime(2019, 1, 28)
    january_late_plan = Plan(
        payment_plan_id=payment_plan.id,
        amount=1000,
        type=1,  # LATE
        due_date=due_date,
    )
    db.session.add(january_late_plan)

    # create plan
    due_date = datetime(2019, 1, 29)
    january_late_plan2 = Plan(
        payment_plan_id=payment_plan.id,
        amount=1000,
        type=1,  # LATE
        due_date=due_date,
    )
    db.session.add(january_late_plan2)

    # create plan
    due_date = datetime(2019, 2, 25)
    february_plan = Plan(
        payment_plan_id=payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(february_plan)

    # create plan
    due_date = datetime(2019, 3, 25)
    march_plan = Plan(
        payment_plan_id=payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(march_plan)
    db.session.commit()

    assert len(payment_plan.plans) == 5

    # try query all amount from january
    current_due_date = datetime(2019, 1, 25)
    next_due_date = current_due_date + relativedelta.relativedelta(months=1)
    total_payment = (
        Plan.query.with_entities(func.sum(Plan.amount).label("total_amount"))
        .filter(Plan.due_date < next_due_date)
        .first()[0]
    )
    assert total_payment == 12000

def test_payment_plan_february():
    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()
    # add balance here
    wallet.add_balance(1000)

    # create payment plan
    payment_plan = PaymentPlan(
        destination="some-bank-account-number", wallet_id=wallet.id
    )
    db.session.add(payment_plan)
    db.session.commit()

    # create plan
    due_date = datetime(2019, 3, 28)
    february_plan = Plan(
        payment_plan_id=payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(february_plan)

    # create late plan
    due_date = datetime(2019, 3, 29)
    february_late_plan = Plan(
        payment_plan_id=payment_plan.id, amount=1000, due_date=due_date
    )
    db.session.add(february_late_plan)

    # create late plan
    due_date = datetime(2019, 4, 2)
    february_late_plan2 = Plan(
        payment_plan_id=payment_plan.id, amount=1000, due_date=due_date
    )
    db.session.add(february_late_plan2)

    # create plan
    due_date = datetime(2019, 5, 28)
    march_plan = Plan(
        payment_plan_id=payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(march_plan)
    db.session.commit()

    assert len(payment_plan.plans) == 4

    # try query all amount from january
    current_due_date = datetime(2019, 3, 28)
    next_due_date = current_due_date + relativedelta.relativedelta(months=1)
    total_payment = (
        Plan.query.with_entities(func.sum(Plan.amount).label("total_amount"))
        .filter(Plan.due_date < next_due_date)
        .first()[0]
    )
    assert total_payment == 12000

def test_payment_modana_cicil_february():
    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()
    # add balance here
    wallet.add_balance(1000)

    # create payment plan
    quick_loan_payment_plan = PaymentPlan(
        destination="some-bank-account-number", wallet_id=wallet.id
    )
    db.session.add(quick_loan_payment_plan)
    db.session.commit()

    # create plan
    due_date = datetime(2019, 3, 28)
    february_plan = Plan(
        payment_plan_id=quick_loan_payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(february_plan)

    # create late plan
    due_date = datetime(2019, 3, 29)
    february_late_plan = Plan(
        payment_plan_id=quick_loan_payment_plan.id, amount=1000, due_date=due_date
    )
    db.session.add(february_late_plan)

    # try query all amount from january
    current_due_date = datetime(2019, 3, 28)
    next_due_date = current_due_date + relativedelta.relativedelta(months=1)
    total_payment = (
        Plan.query.with_entities(func.sum(Plan.amount).label("total_amount"))
        .filter(
            Plan.payment_plan_id == february_plan.payment_plan_id,
            Plan.due_date < next_due_date,
        )
        .first()[0]
    )
    assert total_payment == 11000

    # create payment plan
    loan_payment_plan = PaymentPlan(
        destination="some-bank-account-number", wallet_id=wallet.id
    )
    db.session.add(loan_payment_plan)

    # create plan
    due_date = datetime(2019, 3, 28)
    february_plan = Plan(
        payment_plan_id=loan_payment_plan.id, amount=5000, due_date=due_date
    )
    db.session.add(february_plan)

    # create late plan
    due_date = datetime(2019, 3, 29)
    february_late_plan2 = Plan(
        payment_plan_id=loan_payment_plan.id, amount=500, due_date=due_date
    )
    db.session.add(february_late_plan2)
    db.session.commit()

def test_payment_plan_total():
    # need to make sure if payment plan is FAIL STOP PAID not calculate
    # total

    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()
    # add balance here
    wallet.add_balance(1000)

    # create payment plan
    quick_loan_payment_plan = PaymentPlan(
        destination="some-bank-account-number", wallet_id=wallet.id
    )
    db.session.add(quick_loan_payment_plan)
    db.session.commit()

    # create plan
    due_date = datetime.utcnow()
    february_plan = Plan(
        payment_plan_id=quick_loan_payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(february_plan)

    # create late plan
    due_date = datetime.utcnow() + timedelta(days=1)
    february_late_plan = Plan(
        payment_plan_id=quick_loan_payment_plan.id, amount=1000, due_date=due_date
    )
    db.session.add(february_late_plan)
    db.session.commit()

    total, result = PaymentPlan.total(february_plan)
    assert total == 11000

    # create plan
    due_date = datetime.utcnow() + timedelta(days=1, weeks=4)
    march_plan = Plan(
        payment_plan_id=quick_loan_payment_plan.id,
        amount=10000,
        status=3,  # paid
        due_date=due_date,
    )
    db.session.add(march_plan)

    # create late plan
    due_date = datetime.utcnow() + timedelta(days=2, weeks=4)
    march_late_plan = Plan(
        payment_plan_id=quick_loan_payment_plan.id,
        amount=1000,
        status=3,  # paidm
        due_date=due_date,
    )
    db.session.add(march_late_plan)
    db.session.commit()

    total, plans = PaymentPlan.total(march_plan)
    assert total == 0

    plan = PaymentPlan.check_payment(wallet)

def test_payment_plan_total_duplicate():
    # need to make sure if payment plan is FAIL STOP PAID not calculate
    # total

    # create dummy wallet
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()
    # add balance here
    wallet.add_balance(1000)

    # create payment plan
    quick_loan_payment_plan = PaymentPlan(
        destination="some-bank-account-number", wallet_id=wallet.id
    )
    db.session.add(quick_loan_payment_plan)
    db.session.commit()

    # create plan
    due_date = datetime.utcnow() + timedelta(days=10)
    february_plan = Plan(
        payment_plan_id=quick_loan_payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(february_plan)

    # create plan
    due_date = datetime.utcnow()
    february_plan = Plan(
        payment_plan_id=quick_loan_payment_plan.id, amount=10000, due_date=due_date
    )
    db.session.add(february_plan)
    db.session.commit()

    # total, result = PaymentPlan.total(february_plan)
    # .assertEqual(total, 11000)

    plan = PaymentPlan.check_payment(wallet)
    print(plan)
'''
