"""
    Models
    ___________
    This is module contain all class models that required
"""
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=no-name-in-module
# pylint: disable=no-member
import secrets
import random
import uuid

from datetime import datetime, timedelta
from dateutil import relativedelta

import pytz
import jwt

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import asc, func
from sqlalchemy.dialects.postgresql import UUID

from app.api import db

# const
from app.api.const import WALLET, JWT, VIRTUAL_ACCOUNT

# external config
from app.config.external.bank import BNI_ECOLLECTION
from app.config import config

# exceptions
from app.api.error.authentication import (
    RevokedTokenError,
    SignatureExpiredError,
    InvalidTokenError,
    EmptyPayloadError,
)

now = datetime.utcnow


def uid():
    """ generate uuid """
    return uuid.uuid4()


# end def


def string_uid():
    """ generate string uuid """
    return str(uuid.uuid4())


# end def


class Role(db.Model):
    """
        This is class that represent Role Database Object
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(24))
    created_at = db.Column(db.DateTime, default=now)
    status = db.Column(db.Boolean, default=True)
    user = db.relationship("User", back_populates="role")

    def __repr__(self):
        return "<Role {} {} {}>".format(self.id, self.description, self.status)

    # end def


# end class


class User(db.Model):
    """
        This is class that represent User Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    username = db.Column(db.String(144), unique=True)
    name = db.Column(db.String(144))
    phone_ext = db.Column(db.String(3))  # phone extension
    phone_number = db.Column(db.String(14), unique=True)
    email = db.Column(db.String(144), unique=True)
    created_at = db.Column(db.DateTime, default=now)  # UTC
    password_hash = db.Column(db.String(128))  # hashed password
    status = db.Column(db.Integer, default=1)  # active
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship(
        "Role", back_populates="user", cascade="delete"
    )  # one to one
    wallets = db.relationship(
        "Wallet", back_populates="user", cascade="delete"
    )  # one to many
    bank_accounts = db.relationship(
        "BankAccount", back_populates="user", cascade="delete"
    )  # one to N

    def __repr__(self):
        return "<User {} {} {} {}>".format(
            self.username, self.name, self.phone_number, self.email
        )

    # end def

    def set_password(self, password):
        """
            Function to set hashed password
            args :
                password -- password
        """
        self.password_hash = generate_password_hash(password)

    # end def

    def check_password(self, password):
        """
            Function to check hashed password
            args :
                password -- password
        """
        return check_password_hash(self.password_hash, password)

    # end def

    def get_phone_number(self):
        """
            Function to return phone number as msisdn format
        """
        return str(self.phone_ext) + str(self.msisdn)

    # end def

    @staticmethod
    def encode_token(token_type, user_id):
        """
            Function to create JWT Token
            args :
                token_type -- Access / Refresh
                user_id -- User identity
                role -- User Role
        """
        if token_type == "ACCESS":
            exp = datetime.utcnow() + timedelta(minutes=JWT["ACCESS_EXPIRE"])
        elif token_type == "REFRESH":
            exp = datetime.utcnow() + timedelta(days=JWT["ACCESS_EXPIRE"])
        # end if

        payload = {
            "exp": exp,
            "iat": datetime.utcnow(),
            "sub": str(user_id),
            "type": token_type,
        }
        return jwt.encode(payload, JWT["SECRET"], JWT["ALGORITHM"])

    @staticmethod
    def decode_token(token):
        """
            Function to decode JWT Token
            args :
                token -- Jwt token
        """
        try:
            payload = jwt.decode(token, JWT["SECRET"], algorithms=JWT["ALGORITHM"])
            blacklist_status = BlacklistToken.is_blacklisted(token)
            if blacklist_status:
                raise RevokedTokenError
            if not payload:
                raise EmptyPayloadError
        except jwt.ExpiredSignatureError as error:
            raise SignatureExpiredError(error)
        except jwt.InvalidTokenError as error:
            raise InvalidTokenError(error)
        return payload


class Wallet(db.Model):
    """
        This is class that represent Wallet Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    created_at = db.Column(db.DateTime, default=now)  # UTC
    label = db.Column(db.String(100))
    pin_hash = db.Column(db.String(128))
    status = db.Column(db.Integer, default=1)  # active
    balance = db.Column(db.Float, default=0)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    user = db.relationship(
        "User", back_populates="wallets", cascade="delete"
    )  # many to one
    virtual_accounts = db.relationship(
        "VirtualAccount", cascade="delete"
    )  # one to many
    forgot_pin = db.relationship("ForgotPin", cascade="delete")  # one to many
    incorrect_pin = db.relationship("IncorrectPin", cascade="delete")  # one to many
    wallet_lock = db.relationship("WalletLock", cascade="delete")  # one to many
    withdraw = db.relationship("Withdraw", cascade="delete")  # one to many
    payment_plans = db.relationship(
        "PaymentPlan", back_populates="wallet", cascade="delete"
    )  # one to many
    transactions = db.relationship(
        "Transaction", back_populates="wallet", cascade="delete"
    )  # one to many

    def __repr__(self):
        return "<Wallet {} {} {}>".format(self.id, self.balance, self.user_id)

    # end def

    def check_balance(self):
        """
            Function to return wallet balance
        """
        return self.balance

    # end def

    def is_unlocked(self):
        """
            Function to return wallet lock status
        """
        wallet_lock = WalletLock.query.filter(
            WalletLock.wallet_id == self.id,
            WalletLock.lock_until > datetime.now(),
            WalletLock.status == True,  # pylint:disable=singleton-comparison
        ).first()
        # if is found then it means locked, but it ifs not it mean not unlocked
        return bool(not wallet_lock)

    # end def

    def add_balance(self, amount):
        """
            Function to add wallet balance
        """
        self.balance = self.balance + float(amount)

    # end def

    def lock(self):
        """
            Function to lock wallet
        """
        # first check if there are already existing lock or not
        wallet_lock = WalletLock.query.filter(
            WalletLock.wallet_id == self.id,
            WalletLock.lock_until > datetime.now(),
            WalletLock.status == True,  # pylint:disable=singleton-comparison
        ).first()

        if wallet_lock is None:
            # add lock record
            lock_until = datetime.now() + timedelta(minutes=int(WALLET["LOCK_TIMEOUT"]))

            wallet_lock = WalletLock(wallet_id=self.id, lock_until=lock_until)
            db.session.add(wallet_lock)
            db.session.commit()
        # end if

    # end def

    def unlock(self):
        """
            Function to unlock wallet
        """
        wallet_lock = WalletLock.query.filter(
            WalletLock.wallet_id == self.id,
            WalletLock.lock_until > datetime.now(),
            WalletLock.status == True,  # pylint:disable=singleton-comparison
        ).first()
        # unlock it here
        wallet_lock.status = False
        db.session.commit()

    # end def

    def set_pin(self, pin):
        """
            Function to set wallet pin
        """
        self.pin_hash = generate_password_hash(pin)

    # end def

    def check_pin(self, pin):
        """
            Function to check wallet pin
        """
        status = "INCORRECT"

        # first check pin hash
        is_pin_correct = check_password_hash(self.pin_hash, pin)
        # second check is there incorrect pin record or not
        incorrect_record = IncorrectPin.query.filter(
            IncorrectPin.wallet_id == self.id, IncorrectPin.valid_until > datetime.now()
        ).first()
        # if pin incorrect
        if is_pin_correct is False:
            if incorrect_record is None:
                # create first incorrect record here
                # that valid for certain amount of time
                valid_until = datetime.now() + timedelta(
                    minutes=int(WALLET["INCORRECT_TIMEOUT"])
                )
                incorrect_record = IncorrectPin(
                    wallet_id=self.id, valid_until=valid_until
                )
                db.session.add(incorrect_record)
                db.session.commit()
            else:
                # if its already exist increment the attempt
                incorrect_record.attempt = incorrect_record.attempt + 1
                # print("number of attempt: {}".format(incorrect_record.attempt))
                if incorrect_record.attempt > int(WALLET["INCORRECT_RETRY"]):
                    if self.is_unlocked() is not True:
                        status = "LOCKED"
                    else:
                        status = "MAX_ATTEMPT"
                        # lock the account
                        self.lock()
                    # end if
                # end if
                db.session.commit()
        else:
            if self.is_unlocked() is not True:
                status = "LOCKED"
            else:
                status = "CORRECT"
            # end if
        # end if
        return status

    # end def

    @staticmethod
    def is_owned(user_id, wallet_id):
        """
            Function to check are the user is really the owner of this wallet
        """
        result = Wallet.query.filter_by(user_id=user_id, id=wallet_id).first()
        return bool(result)

    # end def

    @staticmethod
    def total_balance():
        """ used to query all wallet balance inside system """
        total_balance = Wallet.query.with_entities(
            func.sum(Wallet.balance).label("total_balance")
        ).scalar()
        return total_balance


# end class


class VaType(db.Model):
    """
        This is class that represent VaType Database Object
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(24))
    created_at = db.Column(db.DateTime, default=now)
    status = db.Column(db.Boolean, default=True)
    virtual_account = db.relationship(
        "VirtualAccount", back_populates="va_type", cascade="delete"
    )

    def __repr__(self):
        return "<VaType {} {} {}>".format(self.id, self.key, self.status)

    # end def


# end class


class VaLog(db.Model):
    """
        This is class that represent Virtual Account Log Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    status = db.Column(db.Boolean, default=False)  # to show is the operation success or not
    created_at = db.Column(db.DateTime, default=now)  # UTC
    balance = db.Column(db.Float, default=0)
    virtual_account_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("virtual_account.id")
    )
    virtual_account = db.relationship(
        "VirtualAccount", back_populates="logs", cascade="delete"
    )  # many to one

    def __repr__(self):
        return "<VaLog {} {} {}>".format(self.id, self.balance, self.virtual_account)

    # end def


class Bank(db.Model):
    """
        This is class that represent Bank Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    key = db.Column(db.String(24))  # bank_key
    name = db.Column(db.String(100))  # bank_name
    code = db.Column(db.String(100))  # bank_code
    rtgs = db.Column(db.String(100))  # RTGS Code
    created_at = db.Column(db.DateTime, default=now)  # UTC
    status = db.Column(db.Boolean, default=True)  # active / inactive
    virtual_account = db.relationship(
        "VirtualAccount", back_populates="bank"
    )  # one to many
    bank_accounts = db.relationship("BankAccount", back_populates="bank")  # one to many
    payment_channels = db.relationship(
        "PaymentChannel", back_populates="bank"
    )  # one to many

    def __repr__(self):
        return "<Bank {} {} {} {} {}>".format(
            self.id, self.name, self.code, self.rtgs, self.status
        )

    # end def


# end class


class BankAccount(db.Model):
    """
        This is class that represent Bank Account Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    label = db.Column(db.String(30))  # account label
    name = db.Column(db.String(144))  # bank account name
    account_no = db.Column(db.String(30))  # bank account no
    created_at = db.Column(db.DateTime, default=now)  # UTC
    status = db.Column(db.Boolean, default=True)  # active / inactive
    bank_id = db.Column(UUID(as_uuid=True), db.ForeignKey("bank.id"))
    bank = db.relationship("Bank", back_populates="bank_accounts")  # one to one
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="bank_accounts")  # one to one

    def __repr__(self):
        return "<BankAccount {} {} {}>".format(self.id, self.name, self.status)

    # end def


# end class


class PaymentChannel(db.Model):
    """
        This is class that represent Payment Channel Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    name = db.Column(db.String(100))  # payment channel name
    key = db.Column(db.String(100))  # payment channel key
    channel_type = db.Column(db.String(100))  # VIRTUAL ACCOUNT / NORMAL TRANSFER
    created_at = db.Column(db.DateTime, default=now)  # UTC
    status = db.Column(db.Boolean, default=True)  # ACTIVE / INACTIVE
    bank_id = db.Column(UUID(as_uuid=True), db.ForeignKey("bank.id"))
    bank = db.relationship("Bank", back_populates="payment_channels")  # many to one
    payments = db.relationship(
        "Payment", back_populates="payment_channel"
    )  # one to many

    def __repr__(self):
        return "<PaymentChannel {} {} {} {}>".format(
            self.id, self.name, self.key, self.status
        )

    # end def


# end class


class Payment(db.Model):
    """
        This is class that represent Payment Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    source_account = db.Column(
        db.String(100)
    )  # bank account number / wallet / virtual acount
    to = db.Column(db.String(100))  # bank account number / wallet / virtual acount
    ref_number = db.Column(db.String(100), unique=True)  # journal number from the bank
    amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=now)  # UTC
    payment_type = db.Column(db.Boolean, default=True)  # True = Credit / False = Debit
    status = db.Column(db.Integer, default=0)  # PENDING / COMPLETED / REFUNDED / FAILED
    channel_id = db.Column(UUID(as_uuid=True), db.ForeignKey("payment_channel.id"))
    payment_channel = db.relationship(
        "PaymentChannel", back_populates="payments", uselist=False
    )  # one to one
    transaction = db.relationship(
        "Transaction", back_populates="payment", uselist=False
    )  # one to one
    log = db.relationship("Log", back_populates="payment", uselist=False)  # one to one

    def __repr__(self):
        return "<Payment {} {} {} {} {} {}>".format(
            self.source_account,
            self.to,
            self.payment_type,
            self.ref_number,
            self.amount,
            self.status,
        )

    # end def

    def load(self, generator):
        # interface for factory method
        generator.load(self)


# end class


class VirtualAccount(db.Model):
    """
        This is class that represent Virtual Account Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    account_no = db.Column(db.BigInteger)
    trx_id = db.Column(db.BigInteger, unique=True)
    amount = db.Column(db.Float, default=0)
    name = db.Column(db.String(144))
    datetime_expired = db.Column(db.DateTime)
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=now)
    wallet_id = db.Column(UUID(as_uuid=True), db.ForeignKey("wallet.id"))
    wallet = db.relationship(
        "Wallet", back_populates="virtual_accounts", cascade="delete"
    )
    va_type_id = db.Column(db.Integer, db.ForeignKey("va_type.id"))
    va_type = db.relationship(
        "VaType", back_populates="virtual_account", cascade="delete"
    )
    bank_id = db.Column(UUID(as_uuid=True), db.ForeignKey("bank.id"))
    bank = db.relationship("Bank", back_populates="virtual_account", cascade="delete")
    logs = db.relationship("VaLog", back_populates="virtual_account", cascade="delete")

    TIMEZONE = pytz.timezone("Asia/Jakarta")

    def __repr__(self):
        return "<VirtualAccount {} {} {} {} {} {}>".format(
            self.account_no,
            self.trx_id,
            self.name,
            self.status,
            self.va_type,
            self.bank_id,
        )

    # end def

    def is_unlocked(self):
        """ this is function to check is the va unlocked or not """
        return self.status

    # end def

    def lock(self):
        """ this is function to check is the va locked or not """
        self.status = 3

    # end def

    def unlock(self):
        """ this is function to check is the va locked or not """
        self.status = 1

    # end def

    def get_datetime_expired(self, bank_name, va_type):
        """ function to set virtual account datetime_expired based on which
        bank and which type"""
        timeout = VIRTUAL_ACCOUNT[bank_name]

        if va_type == "CREDIT":
            datetime_expired = datetime.now(self.TIMEZONE) + timedelta(
                hours=timeout["CREDIT_VA_TIMEOUT"]
            )
        elif va_type == "DEBIT":
            datetime_expired = datetime.now(self.TIMEZONE) + timedelta(
                minutes=timeout["DEBIT_VA_TIMEOUT"]
            )
        # end if
        self.datetime_expired = datetime_expired
        return str(int(datetime_expired.timestamp()))

    # end def

    def generate_va_number(self):
        """
            function to generate va number
        """
        account_no = None
        # BNI VA Number
        bank = Bank.query.filter_by(id=self.bank_id).first()
        if bank.code == "009":
            while True:
                fixed = BNI_ECOLLECTION["VA_PREFIX"]
                length = BNI_ECOLLECTION["VA_LENGTH"]

                va_type = VaType.query.filter_by(id=self.va_type_id).first()
                if va_type.key == "CREDIT":
                    client_id = BNI_ECOLLECTION["CREDIT_CLIENT_ID"]
                else:
                    client_id = BNI_ECOLLECTION["DEBIT_CLIENT_ID"]
                # end if

                # calculate fixed length first
                prefix = len(fixed) + len(client_id)
                # calulcate free number
                random_length = length - prefix
                # generate 00000000 + 1
                zeroes = "0" * (int(random_length) - 1)
                start_point = int("1" + zeroes)
                # generate 999999999999
                end_point = int("9" * random_length)
                # generate random number between
                suffix = random.randint(start_point, end_point)
                account_no = str(fixed) + str(client_id) + str(suffix)

                result = VirtualAccount.query.filter_by(
                    account_no=int(account_no)
                ).first()
                if result is None:
                    break
                # end if
            # end while
        self.account_no = int(account_no)
        return account_no

    # end def

    def generate_trx_id(self):
        """
            function to generate trx_id
        """
        trx_id = None
        while True:
            trx_id = random.randint(100000000, 999999999)
            result = VirtualAccount.query.filter_by(trx_id=trx_id).first()
            if result is None:
                break
            # end if
        # end while
        self.trx_id = int(trx_id)
        return trx_id

    # end def


# end class


class Log(db.Model):
    """ Used to maintain payment state """

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    state = db.Column(db.Integer, default=0)  # init, done, cancelled
    created_at = db.Column(db.DateTime, default=now)  # UTC
    payment_id = db.Column(UUID(as_uuid=True), db.ForeignKey("payment.id"))
    payment = db.relationship("Payment", back_populates="log")

    def __repr__(self):
        return "<Log {} {} {}".format(self.id, self.state, self.payment_id)


class TransactionNote(db.Model):
    """
        This is class that represent Transaction Notes Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    key = db.Column(db.String(100), unique=True)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=now)

    def __repr__(self):
        return "<TransactionNotes {} {} {}>".format(self.id, self.key, self.notes)


class TransactionType(db.Model):
    """
        This is class that represent Transaction Type Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    key = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=now)
    transaction = db.relationship("Transaction", back_populates="transaction_type")

    def __repr__(self):
        return "<TransactionType {} {} {}>".format(self.id, self.key, self.description)


class Transaction(db.Model):
    """
        This is class that represent Transaction Database Object
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    wallet_id = db.Column(UUID(as_uuid=True), db.ForeignKey("wallet.id"))
    balance = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, default=0)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=now)  # UTC
    payment_id = db.Column(UUID(as_uuid=True), db.ForeignKey("payment.id"))
    payment = db.relationship(
        "Payment", back_populates="transaction", uselist=False
    )  # one to one
    transaction_type_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("transaction_type.id")
    )
    transaction_type = db.relationship(
        "TransactionType", back_populates="transaction", uselist=False
    )  # one to one
    wallet = db.relationship(
        "Wallet", back_populates="transactions", uselist=False
    )  # one to one
    transaction_link_id = db.Column(UUID(as_uuid=True), db.ForeignKey("transaction.id"))
    transaction_link = db.relationship("Transaction", remote_side=[id])  # one to one

    def __repr__(self):
        return "<Transaction {} {} {} {} {}>".format(
            self.id, self.wallet_id, self.amount, self.transaction_type, self.notes
        )

    # end def

    def load(self, generator):
        generator.load(self)


# end class

class BlacklistToken(db.Model):
    """
        This is class Model for Blacklisted Token
    """

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=now)

    @staticmethod
    def is_blacklisted(token):
        """
            function to check whether token has been blacklisted or not
            args :
                token -- JWT Token
        """
        result = BlacklistToken.query.filter_by(token=token).first()
        return bool(result)

    def __repr__(self):
        return "<Blacklist Token {} {}>".format(self.id, self.jti)

    # end def


# end class


class ForgotPin(db.Model):
    """
        Class model for Forgot Pin
    """

    id = db.Column(db.Integer, primary_key=True)
    otp_code = db.Column(db.String(120))
    otp_key = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=now)
    valid_until = db.Column(db.DateTime)
    wallet_id = db.Column(UUID(as_uuid=True), db.ForeignKey("wallet.id"))
    status = db.Column(db.Boolean, default=False)  # done | pending

    def __repr__(self):
        return "<ForgotPin {} {} {} {}>".format(
            self.id, self.wallet_id, self.otp_code, self.status
        )

    # end def

    def set_otp_code(self, otp_code):
        """
            function to store hashed otp code
            args :
                otp_code -- code that going to send to user inbox
        """
        self.otp_code = generate_password_hash(otp_code)

    # end def

    def check_otp_code(self, otp_code):
        """
            function to check hashed otp code
            args :
                otp_code -- code that going to send to user inbox
        """
        return check_password_hash(self.otp_code, otp_code)

    # end def

    def generate_otp_key(self):
        """
            function to generate otp_key
        """
        otp_key = secrets.token_hex(16)
        self.otp_key = otp_key
        return otp_key

    # end def


# end class


class Withdraw(db.Model):
    """
        Class that represent Withdraw Database Model
    """

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=now)
    valid_until = db.Column(db.DateTime)
    wallet_id = db.Column(UUID(as_uuid=True), db.ForeignKey("wallet.id"))

    def __repr__(self):
        return "<Withdraw {} {} {} {}>".format(
            self.id, self.amount, self.wallet_id, self.status
        )

    # end def


# end class


class IncorrectPin(db.Model):
    """
        Class model for Wallet Pin
    """

    id = db.Column(db.Integer, primary_key=True)
    attempt = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=now)
    valid_until = db.Column(db.DateTime)
    locked = db.Column(db.Boolean, default=False)
    wallet_id = db.Column(UUID(as_uuid=True), db.ForeignKey("wallet.id"))

    def __repr__(self):
        return "<IncorrectPin {} {} {}>".format(self.id, self.attempt, self.wallet_id)

    # end def


class WalletLock(db.Model):
    """
        Class model for Wallet Lock
    """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=now)
    lock_until = db.Column(db.DateTime)
    status = db.Column(db.Boolean, default=True)  # ACTIVE | RELEASE
    wallet_id = db.Column(UUID(as_uuid=True), db.ForeignKey("wallet.id"))

    def __repr__(self):
        return "<WalletLock {} {} {}>".format(
            self.created_at, self.lock_until, self.wallet_id
        )

    # end def


class PaymentPlan(db.Model):
    """
        Class model for Payment Plan
    """

    id = db.Column(db.String(255), unique=True, primary_key=True, default=string_uid)
    destination = db.Column(db.String(120))  # Wallet ID | Bank Account
    wallet_id = db.Column(UUID(as_uuid=True), db.ForeignKey("wallet.id"))
    wallet = db.relationship("Wallet", back_populates="payment_plans")  # many to one
    method = db.Column(db.Integer, default=0)  # AUTO | AUTO_DEBIT | AUTO_PAY
    status = db.Column(db.Boolean, default=True)  # ACTIVE | STATUS
    created_at = db.Column(db.DateTime, default=now)
    plans = db.relationship(
        "Plan", back_populates="payment_plan", passive_deletes=True
    )  # one to many

    def __repr__(self):
        return "<PaymentPlan {} {} {} {}>".format(
            self.destination, self.wallet, self.status, self.plans
        )

    # end def

    @staticmethod
    def check_payment(wallet):
        """ look up using wallet and check if there's any payment plan or not """
        plan = (
            Plan.query.join(PaymentPlan)
            .filter(
                PaymentPlan.wallet_id == wallet.id,
                PaymentPlan.method != 1,
                Plan.type == 0,
                Plan.status.in_([0, 1, 2]),
            )
            .order_by(asc(Plan.due_date))
            .first()
        )
        return plan

    # end def

    @staticmethod
    def total(plan):
        """  calculate total payment plan amount for that specific amount until
        the due_date """
        next_due_date = plan.due_date + relativedelta.relativedelta(months=1)
        plans = Plan.query.filter(
            Plan.payment_plan_id == plan.payment_plan_id,
            Plan.status.in_([0, 1, 2]),  # only calculate if its pending|retry|started
            Plan.due_date >= plan.due_date,
            Plan.due_date < next_due_date,
        ).all()
        # calculate total payment here
        total_payment = 0
        for plan_ in plans:
            total_payment = total_payment + plan_.amount
        # end for
        return total_payment, plans

    # end def


# end class


class Plan(db.Model):
    """
        Class model for Plan
    """

    id = db.Column(db.String(255), unique=True, primary_key=True, default=string_uid)
    amount = db.Column(db.Float)  # amount
    type = db.Column(db.Integer, default=0)  # MAIN | LATE | DLL
    status = db.Column(db.Integer, default=0)  # PENDING| RETRY | SENDING | FAIL
    due_date = db.Column(db.DateTime)
    payment_plan_id = db.Column(
        db.String(255), db.ForeignKey("payment_plan.id", ondelete="CASCADE")
    )
    payment_plan = db.relationship("PaymentPlan", back_populates="plans")  # many to one
    created_at = db.Column(db.DateTime, default=now)

    def __repr__(self):
        return "<Plan {} {} {} {} {}>".format(
            self.payment_plan.wallet, self.amount, self.type, self.status, self.due_date
        )

    # end def


class ApiKey(db.Model):
    """
        Class model for Api Key
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    name = db.Column(db.String(255))  # amount
    status = db.Column(db.Integer, default=0)  # PENDING| RETRY | SENDING | FAIL
    created_at = db.Column(db.DateTime, default=now)

    def __repr__(self):
        return "<ApiKey {} {} {}>".format(self.id, self.name, self.status)

    # end def


class BalanceLog(db.Model):
    """
        This is class that represent balance log
        to keep track our system balance with external party
    """

    id = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uid)
    created_at = db.Column(db.DateTime, default=now)  # UTC
    internal_balance = db.Column(db.Float, default=0)
    account_no = db.Column(db.String(100))
    balance = db.Column(db.Float, default=0)
    is_match = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<BalanceLog {} {} {} {} {}>".format(
            self.id, self.account_no, self.internal_balance, self.balance, self.is_match
        )

    # end def
