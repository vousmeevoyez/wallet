""" 
    Models
    ___________
    This is module contain all class models that required
"""
#pylint: disable=bad-whitespace
#pylint: disable=line-too-long
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=too-few-public-methods

from datetime import datetime, timedelta
import pytz
import secrets
import random
import uuid
import jwt

from sqlalchemy.dialects.postgresql import UUID

from werkzeug.security import generate_password_hash 
from werkzeug.security import check_password_hash

from app.api import db
from app.config import config

# exceptions
from app.api.error.authentication import RevokedTokenError
from app.api.error.authentication import SignatureExpiredError
from app.api.error.authentication import InvalidTokenError
from app.api.error.authentication import EmptyPayloadError

now = datetime.utcnow()

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
WALLET_CONFIG = config.Config.WALLET_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
JWT_CONFIG = config.Config.JWT_CONFIG
VIRTUAL_ACCOUNT_CONFIG = config.Config.VIRTUAL_ACCOUNT_CONFIG

def uid():
    return uuid.uuid4()

class Role(db.Model):
    """
        This is class that represent Role Database Object
    """
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(24))
    created_at  = db.Column(db.DateTime, default=now)
    status      = db.Column(db.Boolean, default=True)
    user        = db.relationship("User", back_populates="role")

    def __repr__(self):
        return '<Role {} {} {}>'.format(self.id, self.description, self.status)

class User(db.Model):
    """
        This is class that represent User Database Object
    """
    id              = db.Column(UUID(as_uuid=True), unique=True,
                                primary_key=True, default=uid)
    username        = db.Column(db.String(144), unique=True)
    name            = db.Column(db.String(144))
    phone_ext       = db.Column(db.String(3)) # phone extension
    phone_number    = db.Column(db.String(14), unique=True)
    email           = db.Column(db.String(144), unique=True)
    created_at      = db.Column(db.DateTime, default=now) # UTC
    password_hash   = db.Column(db.String(128)) # hashed password
    status          = db.Column(db.Integer, default=1) # active
    role_id         = db.Column(db.Integer, db.ForeignKey("role.id"))
    role            = db.relationship("Role", back_populates="user") # one to one
    wallets         = db.relationship("Wallet", back_populates="user", cascade="delete") # one to many
    bank_accounts   = db.relationship("BankAccount", back_populates="user", cascade="delete") # one to many

    def __repr__(self):
        return '<User {} {} {} {}>'.format(self.username,
                                           self.name, self.phone_number, self.email,
                                          )

    def set_password(self, password):
        """
            Function to set hashed password
            args :
                password -- password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
            Function to check hashed password
            args :
                password -- password
        """
        return check_password_hash(self.password_hash, password)

    def get_phone_number(self):
        """
            Function to return phone number as msisdn format
        """
        return str(self.phone_ext) + str(self.msisdn)

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
            exp = datetime.utcnow() + timedelta(minutes=JWT_CONFIG["ACCESS_EXPIRE"])
        elif token_type == "REFRESH":
            exp = datetime.utcnow() + timedelta(days=JWT_CONFIG["ACCESS_EXPIRE"])

        payload = {
            "exp" : exp,
            "iat" : datetime.utcnow(),
            "sub" : str(user_id),
            "type": token_type,
        }
        return jwt.encode(
            payload,
            JWT_CONFIG["SECRET"],
            JWT_CONFIG["ALGORITHM"]
        )

    @staticmethod
    def decode_token(token):
        """
            Function to decode JWT Token
            args :
                token -- Jwt token
        """
        try:
            payload = jwt.decode(token, JWT_CONFIG["SECRET"],
                                 algorithms=JWT_CONFIG["ALGORITHM"])
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
    id              = db.Column(UUID(as_uuid=True), unique=True,
                                primary_key=True, default=uid)
    created_at       = db.Column(db.DateTime, default=now) # UTC
    label            = db.Column(db.String(100), unique=True)
    pin_hash         = db.Column(db.String(128))
    status           = db.Column(db.Integer, default=1) # active
    balance          = db.Column(db.Float, default=0)
    user_id          = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    user             = db.relationship("User", back_populates="wallets") # many to one
    virtual_accounts = db.relationship("VirtualAccount", cascade="delete") # one to many
    forgot_pin       = db.relationship("ForgotPin") # one to many
    withdraw         = db.relationship("Withdraw") # one to many
    transactions     = db.relationship("Transaction", back_populates="wallet") # one to many

    def __repr__(self):
        return '<Wallet {} {} {}>'.format(self.id, self.balance, self.user_id)
    #end def

    def check_balance(self):
        """
            Function to return wallet balance
        """
        return self.balance
    #end def

    def is_unlocked(self):
        """
            Function to return wallet lock status
        """
        if self.status == 3:
            return False
        else:
            return True
    #end def

    def add_balance(self, amount):
        """
            Function to add wallet balance
        """
        self.balance = self.balance + float(amount)
    #end def

    def lock(self):
        """
            Function to lock wallet
        """
        self.status = 3
    #end def

    def unlock(self):
        """
            Function to unlock wallet
        """
        self.status = 1
    #end def

    def set_pin(self, pin):
        """
            Function to set wallet pin
        """
        self.pin_hash = generate_password_hash(pin)
    #end def

    def check_pin(self, pin):
        """
            Function to check wallet pin
        """
        return check_password_hash(self.pin_hash, pin)
    #end def

    @staticmethod
    def is_owned(user_id, wallet_id):
        """
            Function to check are the user is really the owner of this wallet
        """
        result = Wallet.query.filter_by(user_id=user_id, id=wallet_id).first()
        return bool(result)
    #end def
#end class

class VaType(db.Model):
    """
        This is class that represent VaType Database Object
    """
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key             = db.Column(db.String(24))
    created_at      = db.Column(db.DateTime, default=now)
    status          = db.Column(db.Boolean, default=True)
    virtual_account = db.relationship("VirtualAccount", back_populates="va_type")

    def __repr__(self):
        return '<VaType {} {} {}>'.format(self.id, self.key, self.status)
    #end def
#end class

class Bank(db.Model):
    """
        This is class that represent Bank Database Object
    """
    id              = db.Column(UUID(as_uuid=True), unique=True,
                                primary_key=True, default=uid)
    key             = db.Column(db.String(24)) # bank_key
    name            = db.Column(db.String(100)) # bank_name
    code            = db.Column(db.String(100)) # bank_code
    rtgs            = db.Column(db.String(100)) # RTGS Code
    created_at      = db.Column(db.DateTime, default=now) # UTC
    status          = db.Column(db.Boolean, default=True) # active / inactive
    virtual_account = db.relationship("VirtualAccount", back_populates="bank") # one to many
    bank_accounts   = db.relationship("BankAccount", back_populates="bank") # one to many
    payment_channels= db.relationship("PaymentChannel", back_populates="bank") # one to many

    def __repr__(self):
        return '<Bank {} {} {} {} {}>'.format(self.id, self.name, self.code,
                                              self.rtgs, self.status)
    #end def
#end class

class BankAccount(db.Model):
    """
        This is class that represent Bank Account Database Object
    """
    id         = db.Column(UUID(as_uuid=True), unique=True,
                                primary_key=True, default=uid)
    label      = db.Column(db.String(30), unique=True) # account label
    name       = db.Column(db.String(24), unique=True) # bank account name
    account_no = db.Column(db.String(30), unique=True) # bank account no
    created_at = db.Column(db.DateTime, default=now) # UTC
    status     = db.Column(db.Boolean, default=True) # active / inactive
    bank_id    = db.Column(UUID(as_uuid=True), db.ForeignKey("bank.id"))
    bank       = db.relationship("Bank", back_populates="bank_accounts") # one to one
    user_id    = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    user       = db.relationship("User", back_populates="bank_accounts") # one to one

    def __repr__(self):
        return '<BankAccount {} {} {}>'.format(self.id, self.name, self.status)
    #end def
#end class

class PaymentChannel(db.Model):
    """
        This is class that represent Payment Channel Database Object
    """
    id           = db.Column(UUID(as_uuid=True), unique=True,
                             primary_key=True, default=uid)
    name         = db.Column(db.String(100)) # payment channel name
    key          = db.Column(db.String(100)) # payment channel key
    channel_type = db.Column(db.String(100)) # VIRTUAL ACCOUNT / NORMAL TRANSFER
    created_at   = db.Column(db.DateTime, default=now) # UTC
    status       = db.Column(db.Boolean, default=True) # ACTIVE / INACTIVE
    bank_id      = db.Column(UUID(as_uuid=True), db.ForeignKey("bank.id"))
    bank         = db.relationship("Bank", back_populates="payment_channels") # many to one
    payments     = db.relationship("Payment", back_populates="payment_channel") # one to many

    def __repr__(self):
        return '<PaymentChannel {} {} {} {}>'.format(self.id, self.name, self.key, self.status)
    #end def
#end class

class Payment(db.Model):
    """
        This is class that represent Payment Database Object
    """
    id             = db.Column(UUID(as_uuid=True), unique=True,
                               primary_key=True, default=uid)
    source_account = db.Column(db.String(100)) # can be bank account number / wallet / virtual acount (money comes from)
    to             = db.Column(db.String(100)) # can be bank account number / wallet / virtual acount ( money goes)
    ref_number     = db.Column(db.String(100)) # journal number from the bank
    amount         = db.Column(db.Float)
    created_at     = db.Column(db.DateTime, default=now) # UTC
    payment_type   = db.Column(db.Boolean, default=True) # True = Credit / False = Debit
    status         = db.Column(db.Integer, default=0) # PENDING / COMPLETED / FAILED
    channel_id     = db.Column(UUID(as_uuid=True), db.ForeignKey("payment_channel.id"))
    payment_channel= db.relationship("PaymentChannel", back_populates="payments", uselist=False) # one to one
    transaction    = db.relationship("Transaction", back_populates="payment", uselist=False) # one to one
    log            = db.relationship("Log", back_populates="payment", uselist=False) # one to one

    def __repr__(self):
        return '<Payment {} {} {} {} {} {}>'.format(self.id, self.source_account, self.payment_type,
                                                 self.ref_number, self.amount, self.status)
    #end def
#end class

class VirtualAccount(db.Model):
    """
        This is class that represent Virtual Account Database Object
    """
    id              = db.Column(UUID(as_uuid=True), unique=True,
                                primary_key=True, default=uid)
    account_no      = db.Column(db.BigInteger)
    trx_id          = db.Column(db.BigInteger, unique=True)
    amount          = db.Column(db.Float, default=0)
    name            = db.Column(db.String(144))
    datetime_expired= db.Column(db.DateTime)
    status          = db.Column(db.Integer, default=0)
    created_at      = db.Column(db.DateTime, default=now)
    wallet_id       = db.Column(UUID(as_uuid=True), db.ForeignKey('wallet.id'))
    wallet          = db.relationship("Wallet", back_populates="virtual_accounts", cascade="delete")
    va_type_id      = db.Column(db.Integer, db.ForeignKey("va_type.id"))
    va_type         = db.relationship("VaType", back_populates="virtual_account")
    bank_id         = db.Column(UUID(as_uuid=True), db.ForeignKey("bank.id"))
    bank            = db.relationship("Bank", back_populates="virtual_account")

    TIMEZONE = pytz.timezone("Asia/Jakarta")

    def __repr__(self):
        return '<VirtualAccount {} {} {} {} {} {}>'.format(self.account_no, self.trx_id, self.name, self.status, self.va_type, self.bank_id)
    #end def

    def is_unlocked(self):
        """ this is function to check is the va unlocked or not """
        return self.status
    #end def

    def lock(self):
        """ this is function to check is the va locked or not """
        self.status = 3
    #end def

    def unlock(self):
        """ this is function to check is the va locked or not """
        self.status = 1
    #end def

    def get_datetime_expired(self, bank_name, va_type):
        """ function to set virtual account datetime_expired based on which
        bank and which type"""
        timeout = VIRTUAL_ACCOUNT_CONFIG[bank_name]

        if va_type == "CREDIT":
            datetime_expired = datetime.now(self.TIMEZONE) \
                               + timedelta(hours=timeout["CREDIT_VA_TIMEOUT"])
        elif va_type == "DEBIT":
            datetime_expired = datetime.now(self.TIMEZONE) \
                               + timedelta(minutes=timeout["DEBIT_VA_TIMEOUT"])

        self.datetime_expired = datetime_expired
        return str(int(datetime_expired.timestamp()))
      #end def

    def generate_va_number(self):
        """
            function to generate va number
        """
        account_no = None
        """
            BNI VA Number
        """
        bank = Bank.query.filter_by(id=self.bank_id).first()
        if bank.code == "009":
            while True:
                fixed = BNI_ECOLLECTION_CONFIG["VA_PREFIX"]
                length = BNI_ECOLLECTION_CONFIG["VA_LENGTH"]

                va_type = VaType.query.filter_by(id=self.va_type_id).first()
                if va_type.key == "CREDIT":
                    client_id = BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"]
                else:
                    client_id = BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"]
                #end if

                # calculate fixed length first
                prefix = len(fixed) + len(client_id)
                # calulcate free number
                random_length = length - prefix
                # generate 00000000 + 1
                zeroes = '0' * (int(random_length)-1)
                start_point = int('1' + zeroes)
                # generate 999999999999
                end_point = int('9' * random_length)
                # generate random number between
                suffix = random.randint(
                    start_point,
                    end_point
                )
                account_no = str(fixed) + str(client_id) + str(suffix)

                result = VirtualAccount.query.filter_by(account_no=int(account_no)).first()
                if result is None:
                    break
                #end if
            #end while
        self.account_no = int(account_no)
        return account_no
    #end def

    def generate_trx_id(self):
        """
            function to generate trx_id
        """
        trx_id = None
        while True:
            trx_id = random.randint(
                100000000,
                999999999
            )
            result = VirtualAccount.query.filter_by(trx_id=trx_id).first()
            if result is None:
                break
            #end if
        #end while
        self.trx_id = int(trx_id)
        return trx_id
    #end def
#end class

class Log(db.Model):
    """ Used to maintain payment state """
    id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    state       = db.Column(db.Integer, default=0) # init, done, cancelled
    created_at  = db.Column(db.DateTime, default=now) # UTC
    payment_id  = db.Column(UUID(as_uuid=True), db.ForeignKey("payment.id"))
    payment     = db.relationship("Payment", back_populates="log")

    def __repr__(self):
        return '<Log {} {} {}'.format(self.id, self.state,
                                      self.payment_id)

class Transaction(db.Model):
    """
        This is class that represent Transaction Database Object
    """
    id                 = db.Column(UUID(as_uuid=True), unique=True,
                                   primary_key=True, default=uid)
    wallet_id          = db.Column(UUID(as_uuid=True), db.ForeignKey('wallet.id'))
    amount             = db.Column(db.Float, default=0)
    transaction_type   = db.Column(db.Integer) # withdraw / deposit / transfer_bank / transfer_va
    notes              = db.Column(db.String(255)) # transaction notes if there are
    created_at         = db.Column(db.DateTime, default=now) # UTC
    payment_id         = db.Column(UUID(as_uuid=True), db.ForeignKey("payment.id"))
    payment            = db.relationship("Payment", back_populates="transaction", uselist=False) # one to one
    wallet             = db.relationship("Wallet", back_populates="transactions", uselist=False) # one to one

    def __repr__(self):
        return '<Transaction {} {} {} {} {}>'.format(self.id, self.wallet_id, self.amount,
                                                     self.transaction_type, self.notes)
    #end def
#end class

class ExternalLog(db.Model):
    """
        This is class that represent External Database Object
    """
    id          = db.Column(db.Integer, primary_key=True)
    status      = db.Column(db.Boolean, default=True)
    resource    = db.Column(db.String(255))
    api_name    = db.Column(db.String(255))
    request     = db.Column(db.JSON)
    response    = db.Column(db.JSON)
    api_type    = db.Column(db.Integer, default=0) # 0 mean outgoing
    created_at  = db.Column(db.DateTime, default=now)
    response_time = db.Column(db.Float, default=0) #seconds

    def set_status(self, status):
        """
            Function to set Log status
            args :
                status -- True / False
        """
        self.status = status
    #end def

    def save_response(self, response):
        """
            Function to set log response
            args :
                response -- Json response
        """
        self.response = response
    #end def

    def save_response_time(self, response_time):
        """
            Function to set log response time
            args :
                response -- Json response
        """
        self.response_time = response_time
    #end def


    def __repr__(self):
        return '<External Log {} {} {} {} {} {}>'.format(self.id, self.resource, self.api_name,
                                                         self.status, self.request, self.response)
    #end def
#end class

class BlacklistToken(db.Model):
    """
        This is class Model for Blacklisted Token
    """
    id          = db.Column(db.Integer, primary_key=True)
    token       = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime, default=now)

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
        return '<Blacklist Token {} {}>'.format(self.id, self.jti)
    #end def
#end class

class ForgotPin(db.Model):
    """
        Class model for Forgot Pin
    """
    id          = db.Column(db.Integer, primary_key=True)
    otp_code    = db.Column(db.String(120))
    otp_key     = db.Column(db.String(120))
    created_at  = db.Column(db.DateTime, default=now)
    valid_until = db.Column(db.DateTime)
    wallet_id   = db.Column(UUID(as_uuid=True), db.ForeignKey('wallet.id'))
    status      = db.Column(db.Boolean, default=False) # done | pending

    def __repr__(self):
        return '<ForgotPin {} {} {} {}>'.format(self.id, self.wallet_id, self.otp_code, self.status)
    #end def

    def set_otp_code(self, otp_code):
        """
            function to store hashed otp code
            args :
                otp_code -- code that going to send to user inbox
        """
        self.otp_code = generate_password_hash(otp_code)
    #end def

    def check_otp_code(self, otp_code):
        """
            function to check hashed otp code
            args :
                otp_code -- code that going to send to user inbox
        """
        return check_password_hash(self.otp_code, otp_code)
    #end def

    def generate_otp_key(self):
        """
            function to generate otp_key
        """
        otp_key = secrets.token_hex(16)
        self.otp_key = otp_key
        return otp_key
    #end def
#end class

class Withdraw(db.Model):
    """
        Class that represent Withdraw Database Model
    """
    id          = db.Column(db.Integer, primary_key=True)
    amount      = db.Column(db.Float)
    created_at  = db.Column(db.DateTime, default=now)
    valid_until = db.Column(db.DateTime)
    wallet_id   = db.Column(UUID(as_uuid=True), db.ForeignKey('wallet.id'))

    def __repr__(self):
        return '<Withdraw {} {} {} {}>'.format(self.id, self.amount, self.wallet_id, self.status)
    #end def
#end class
