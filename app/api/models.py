import secrets
import random
import traceback
import jwt

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from app.api        import db
from app.api.config import config

now = datetime.utcnow()

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
WALLET_CONFIG          = config.Config.WALLET_CONFIG
TRANSACTION_NOTES      = config.Config.TRANSACTION_NOTES
JWT_CONFIG             = config.Config.JWT_CONFIG

class Role(db.Model):
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(24))
    created_at  = db.Column(db.DateTime, default=now)
    status      = db.Column(db.Boolean, default=True)
    user        = db.relationship("User", back_populates="role")

    def __repr__(self):
        return '<Role {} {} {}>'.format(self.id, self.description, self.status)
    #end def
#end class

class User(db.Model):
    id              = db.Column(db.BigInteger, primary_key=True)
    username        = db.Column(db.String(144), unique=True)
    name            = db.Column(db.String(144))
    phone_ext       = db.Column(db.String(3))
    phone_number    = db.Column(db.String(11), unique=True)
    email           = db.Column(db.String(144), unique=True)
    created_at      = db.Column(db.DateTime, default=now)
    password_hash   = db.Column(db.String(128))
    status          = db.Column(db.Boolean, default=True)
    role_id         = db.Column(db.Integer, db.ForeignKey("role.id"))
    role            = db.relationship("Role", back_populates="user")
    wallets         = db.relationship("Wallet", back_populates="user", cascade="delete")
    bank_accounts   = db.relationship("BankAccount", back_populates="user", cascade="delete")

    def __repr__(self):
        return '<User {} {} {} {}>'.format(self.username,
                                     self.name, self.phone_number, self.email,
                                    )
    #end def

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #end def

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    #end def

    def get_phone_number(self):
        return str(self.phone_ext) + str(self.msisdn)
    #end def

    @staticmethod
    def encode_token(token_type, user_id, role):
        try:
            if token_type == "ACCESS":
                exp = datetime.utcnow() + timedelta(minutes=JWT_CONFIG["ACCESS_EXPIRE"])
            elif token_type == "REFRESH":
                exp = datetime.utcnow() + timedelta(days=JWT_CONFIG["ACCESS_EXPIRE"])
            #end if
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
    #end def

    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, JWT_CONFIG["SECRET"])
            blacklist_status = BlacklistToken.is_blacklisted(token)
            if blacklist_status == True:
                return "Token has been revoked"
            else:
                return payload
        except jwt.ExpiredSignatureError:
            return "Signature Expired"
        except jwt.InvalidTokenError:
            return "Invalid Token"
    #end def

#end class

class Wallet(db.Model):
    id               = db.Column(db.BigInteger, primary_key=True)
    created_at       = db.Column(db.DateTime, default=now)
    pin_hash         = db.Column(db.String(128))
    status           = db.Column(db.Boolean, default=True)
    balance          = db.Column(db.Float, default=0)
    user_id          = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    user             = db.relationship("User", back_populates="wallets")
    virtual_accounts = db.relationship("VirtualAccount", cascade="delete")
    forgot_pin       = db.relationship("ForgotPin")

    def __repr__(self):
        return '<Wallet {} {} {}>'.format(self.id, self.balance, self.user_id)
    #end def

    def check_balance(self):
        return self.balance
    #end def

    def is_unlocked(self):
        return self.status
    #end def

    def add_balance(self, amount):
        self.balance = self.balance + float(amount)
    #end def

    def deduct_balance(self, amount):
        self.balance = self.balance - float(amount)
    #end def

    def lock(self):
        self.status = False
    #end def

    def unlock(self):
        if self.status != True:
            self.status = True
    #end def

    def generate_wallet_id(self):
        wallet_id = None
        while True:
            wallet_id_prefix = 11
            wallet_id_suffix = random.randint(
                10000000,
                99999999
            )
            wallet_id = str(wallet_id_prefix) + str(wallet_id_suffix)
            result = Wallet.query.filter_by(id=wallet_id).first()
            if result == None:
                break
            #end if
        #end while
        self.id = int(wallet_id)
        return wallet_id
    #end def

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)
    #end def

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)
    #end def

    @staticmethod
    def is_owned(user_id, wallet_id):
        result = Wallet.query.filter_by(user_id=user_id, id=wallet_id).first()
        return bool(result)
    #end def
#end class

class VaType(db.Model):
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
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key             = db.Column(db.String(24))
    name            = db.Column(db.String(100))
    code            = db.Column(db.String(100))
    created_at      = db.Column(db.DateTime, default=now)
    status          = db.Column(db.Boolean, default=True)
    virtual_account = db.relationship("VirtualAccount", back_populates="bank")
    bank_account    = db.relationship("BankAccount", back_populates="bank")

    def __repr__(self):
        return '<Bank {} {} {}>'.format(self.id, self.name, self.code, self.status)
    #end def
#end class

class BankAccount(db.Model):
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name       = db.Column(db.String(24))
    created_at = db.Column(db.DateTime, default=now)
    status     = db.Column(db.Boolean, default=True)
    bank_id    = db.Column(db.Integer, db.ForeignKey("bank.id"))
    bank       = db.relationship("Bank", back_populates="bank_account")
    user_id    = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    user       = db.relationship("User", back_populates="bank_accounts")

    def __repr__(self):
        return '<BankAccount {} {} {}>'.format(self.id, self.name, self.status)
    #end def
#end class

class VirtualAccount(db.Model):
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
        return self.status
    #end def

    def lock(self):
        self.status = False
    #end def

    def unlock(self):
        if self.status != True:
            self.status = True
    #end def

    def generate_va_number(self):
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
            if result == None:
                break
            #end if
        #end while
        self.id = int(va_id)
        return va_id
    #end def

    def generate_trx_id(self):
        trx_id = None
        while True:
            trx_id = random.randint(
                100000000,
                999999999
            )
            result = VirtualAccount.query.filter_by(trx_id=trx_id).first()
            if result == None:
                break
            #end if
        #end while
        self.trx_id= int(trx_id)
        return trx_id
    #end def

#end class

class Transaction(db.Model):
    id               = db.Column(db.BigInteger, primary_key=True)
    source_id        = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    destination_id   = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    amount           = db.Column(db.Float)
    transaction_type = db.Column(db.Boolean)
    transfer_type    = db.Column(db.Integer)
    notes            = db.Column(db.String(255))
    created_at       = db.Column(db.DateTime, default=now)
    source           = db.relationship("Wallet", foreign_keys=[source_id])
    destination      = db.relationship("Wallet", foreign_keys=[destination_id])

    def __repr__(self):
        return '<Transaction {} {} {} {} {} {}>'.format(self.id, self.source_id, self.amount, self.transaction_type, self.destination_id, self.notes)
    #end def

    def generate_trx_id(self):
        trx_id = None
        while True:
            trx_id = str(random.randint(
                100000000,
                999999999
            ))
            result = Transaction.query.filter_by(id=trx_id).first()
            if result == None:
                break
            #end if
        #end while
        self.id = int(trx_id)
        return trx_id
    #end def
#end class

class ExternalLog(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    status      = db.Column(db.Boolean, default=True)
    resource    = db.Column(db.String(255))
    api_name    = db.Column(db.String(255))
    request     = db.Column(db.JSON)
    response    = db.Column(db.JSON)
    api_type    = db.Column(db.Integer, default=0) # 0 mean outgoing
    created_at  = db.Column(db.DateTime, default=now)

    def set_status(self, status):
        self.status = status
    #end def

    def save_response(self, response):
        self.response = response
    #end def

    def __repr__(self):
        return '<External Log {} {} {} {} {} {}>'.format(self.id, self.resource, self.api_name, self.status, self.request, self.response)
    #end def
#end class

class BlacklistToken(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    token       = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime, default=now)

    @staticmethod
    def is_blacklisted(token):
        result = BlacklistToken.query.filter_by(token=token).first()
        return bool(result)

    def __repr__(self):
        return '<Blacklist Token {} {}>'.format(self.id, self.jti)
    #end def
#end class

class ForgotPin(db.Model):
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
        self.otp_code = generate_password_hash(otp_code)
    #end def

    def check_otp_code(self, otp_code):
        return check_password_hash(self.otp_code, otp_code)
    #end def

    def generate_otp_key(self):
        otp_key = secrets.token_hex(16)
        self.otp_key = otp_key
        return otp_key
    #end def
#end class
