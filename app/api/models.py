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
import secrets
import random
import uuid
import jwt

from werkzeug.security import generate_password_hash 
from werkzeug.security import check_password_hash

from app.api import db
from app.api.config import config

now = datetime.utcnow()

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
WALLET_CONFIG = config.Config.WALLET_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
JWT_CONFIG = config.Config.JWT_CONFIG

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
    id              = db.Column(db.BigInteger, primary_key=True)
    username        = db.Column(db.String(144), unique=True)
    name            = db.Column(db.String(144))
    phone_ext       = db.Column(db.String(3)) # phone extension
    phone_number    = db.Column(db.String(11), unique=True)
    email           = db.Column(db.String(144), unique=True)
    created_at      = db.Column(db.DateTime, default=now) # UTC
    password_hash   = db.Column(db.String(128)) # hashed password
    status          = db.Column(db.Boolean, default=True) # active / inactive
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
    def encode_token(token_type, user_id, role):
        """
            Function to create JWT Token
            args :
                token_type -- Access / Refresh
                user_id -- User identity
                role -- User Role
        """
        try:
            if token_type == "ACCESS":
                exp = datetime.utcnow() + timedelta(minutes=JWT_CONFIG["ACCESS_EXPIRE"])
            elif token_type == "REFRESH":
                exp = datetime.utcnow() + timedelta(days=JWT_CONFIG["ACCESS_EXPIRE"])

            payload = {
                "exp" : exp,
                "iat" : datetime.utcnow(),
                "sub" : user_id,
                "type": token_type,
                "role": role,
            }
            return jwt.encode(
                payload,
                JWT_CONFIG["SECRET"],
                algorithm="HS256"
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_token(token):
        """
            Function to decode JWT Token
            args :
                token -- Jwt token
        """
        try:
            payload = jwt.decode(token, JWT_CONFIG["SECRET"])
            blacklist_status = BlacklistToken.is_blacklisted(token)
            if blacklist_status:
                return "Token has been revoked"
        except jwt.ExpiredSignatureError:
            return "Signature Expired"
        except jwt.InvalidTokenError:
            return "Invalid Token"
        return payload

class Wallet(db.Model):
    """
        This is class that represent Wallet Database Object
    """
    id               = db.Column(db.BigInteger, primary_key=True)
    created_at       = db.Column(db.DateTime, default=now) # UTC
    pin_hash         = db.Column(db.String(128))
    status           = db.Column(db.Boolean, default=True)
    balance          = db.Column(db.Float, default=0)
    user_id          = db.Column(db.BigInteger, db.ForeignKey('user.id'))
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
        return self.status
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
        self.status = False
    #end def

    def unlock(self):
        """
            Function to unlock wallet
        """
        self.status = True
    #end def

    def generate_wallet_id(self):
        """
            Function to generate wallet id
        """
        wallet_id = None
        while True:
            wallet_id_prefix = 11
            wallet_id_suffix = random.randint(
                10000000,
                99999999
            )
            wallet_id = str(wallet_id_prefix) + str(wallet_id_suffix)
            result = Wallet.query.filter_by(id=wallet_id).first()
            if result is None:
                break
            #end if
        #end while
        self.id = int(wallet_id)
        return wallet_id
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
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label      = db.Column(db.String(24), unique=True) # account label
    name       = db.Column(db.String(24), unique=True) # bank account name
    account_no = db.Column(db.String(24), unique=True) # bank account no
    created_at = db.Column(db.DateTime, default=now) # UTC
    status     = db.Column(db.Boolean, default=True) # active / inactive
    bank_id    = db.Column(db.Integer, db.ForeignKey("bank.id"))
    bank       = db.relationship("Bank", back_populates="bank_accounts") # one to one
    user_id    = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    user       = db.relationship("User", back_populates="bank_accounts") # one to one

    def __repr__(self):
        return '<BankAccount {} {} {}>'.format(self.id, self.name, self.status)
    #end def
#end class

class PaymentChannel(db.Model):
    """
        This is class that represent Payment Channel Database Object
    """
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name         = db.Column(db.String(100)) # payment channel name
    key          = db.Column(db.String(100)) # payment channel key
    channel_type = db.Column(db.String(100)) # VIRTUAL ACCOUNT / NORMAL TRANSFER
    created_at   = db.Column(db.DateTime, default=now) # UTC
    status       = db.Column(db.Boolean, default=True) # ACTIVE / INACTIVE
    bank_id      = db.Column(db.Integer, db.ForeignKey("bank.id"))
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
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_account = db.Column(db.String(100)) # can be bank account number / wallet / virtual acount (money comes from)
    to             = db.Column(db.String(100)) # can be bank account number / wallet / virtual acount ( money goes)
    ref_number     = db.Column(db.String(100)) # journal number from the bank
    amount         = db.Column(db.Float)
    created_at     = db.Column(db.DateTime, default=now) # UTC
    payment_type   = db.Column(db.Boolean, default=True) # True = Credit / False = Debit
    status         = db.Column(db.Integer, default=1) # COMPLETED / PENDING / FAILED
    channel_id     = db.Column(db.Integer, db.ForeignKey("payment_channel.id"))
    payment_channel= db.relationship("PaymentChannel", back_populates="payments", uselist=False) # one to one
    transaction    = db.relationship("Transaction", back_populates="payment", uselist=False) # one to one

    def __repr__(self):
        return '<Payment {} {} {} {} {}>'.format(self.id, self.source_account,
                                                 self.ref_number, self.amount, self.status)
    #end def
#end class

class VirtualAccount(db.Model):
    """
        This is class that represent Virtual Account Database Object
    """
    id              = db.Column(db.BigInteger, primary_key=True)
    trx_id          = db.Column(db.BigInteger, unique=True)
    trx_amount      = db.Column(db.Float, default=0)
    name            = db.Column(db.String(144))
    datetime_expired= db.Column(db.DateTime)
    status          = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=now)
    wallet_id       = db.Column(db.BigInteger, db.ForeignKey('wallet.id'))
    wallet          = db.relationship("Wallet", back_populates="virtual_accounts", cascade="delete")
    va_type_id      = db.Column(db.Integer, db.ForeignKey("va_type.id"))
    va_type         = db.relationship("VaType", back_populates="virtual_account")
    bank_id         = db.Column(db.Integer, db.ForeignKey("bank.id"))
    bank            = db.relationship("Bank", back_populates="virtual_account")

    def __repr__(self):
        return '<VirtualAccount {} {} {} {} {}>'.format(self.id, self.trx_id, self.name, self.status, self.va_type)
    #end def

    def is_unlocked(self):
        """ this is function to check is the va unlocked or not """
        return self.status
    #end def

    def lock(self):
        """ this is function to check is the va locked or not """
        self.status = False
    #end def

    def unlock(self):
        """ this is function to check is the va locked or not """
        self.status = True
    #end def

    def generate_va_number(self):
        """
            function to generate va number
        """
        va_id = None

        while True:
            fixed = 988

            va_type = VaType.query.filter_by(id=self.va_type_id).first()

            if va_type.key == "CREDIT":
                client_id = BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"]
            else:
                client_id = BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"]
            #end if
            suffix = random.randint(
                10000000,
                99999999
            )
            va_id = str(fixed) + str(client_id) + str(suffix)
            result = VirtualAccount.query.filter_by(id=int(va_id)).first()
            if result is None:
                break
            #end if
        #end while
        self.id = int(va_id)
        return va_id
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

class MasterTransaction(db.Model):
    """
        used as transaction block to ensure each transaction is safe
    """
    id                    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source                = db.Column(db.String(100)) # can be bank account number / wallet / virtual acount (money comes from)
    destination           = db.Column(db.String(100)) # can be bank account number / wallet / virtual acount (money comes from)
    last_modified         = db.Column(db.DateTime, default=now) # UTC
    amount                = db.Column(db.Float)
    # 0 = INIT , 1 = PENDING , 2 = DONE , 3 = CANCEL
    state                 = db.Column(db.Integer, default=0)
    debit_transaction_id  = db.Column(db.String, db.ForeignKey("transaction.id"))
    credit_transaction_id = db.Column(db.String, db.ForeignKey("transaction.id"))
    debit_transaction     = db.relationship("Transaction", \
                                            uselist=False,
                                            foreign_keys=[debit_transaction_id]) # one to one
    credit_transaction    = db.relationship("Transaction", \
                                            uselist=False,
                                            foreign_keys=[credit_transaction_id]) # one to one

    def __repr__(self):
        return '<MasterTransaction {} {} {} {} {} {} {} >'.format(self.id,\
                                                           self.source,\
                                                           self.destination,\
                                                           self.amount,\
                                                           self.state,\
                                                           self.debit_transaction_id,\
                                                           self.credit_transaction_id\
                                                          )
    #end def

class Transaction(db.Model):
    """
        This is class that represent Transaction Database Object
    """
    id                 = db.Column(db.String(255), primary_key=True)
    wallet_id          = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    amount             = db.Column(db.Float, default=0)
    transaction_type   = db.Column(db.Integer) # withdraw / deposit / transfer_bank / transfer_va
    notes              = db.Column(db.String(255)) # transaction notes if there are
    created_at         = db.Column(db.DateTime, default=now) # UTC
    payment_id         = db.Column(db.Integer, db.ForeignKey("payment.id"))
    payment            = db.relationship("Payment", back_populates="transaction", uselist=False) # one to one
    wallet             = db.relationship("Wallet", back_populates="transactions", uselist=False) # one to one

    def __repr__(self):
        return '<Transaction {} {} {} {} {}>'.format(self.id, self.wallet_id, self.amount,
                                                     self.transaction_type, self.notes)
    #end def

    def generate_trx_id(self):
        """
            function to generate trx_id
        """
        trx_id = str(uuid.uuid4())
        self.id = trx_id
        return trx_id
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
    wallet_id   = db.Column(db.BigInteger, db.ForeignKey('wallet.id'))
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
    wallet_id   = db.Column(db.BigInteger, db.ForeignKey('wallet.id'))

    def __repr__(self):
        return '<Withdraw {} {} {} {}>'.format(self.id, self.amount, self.wallet_id, self.status)
    #end def
#end class
