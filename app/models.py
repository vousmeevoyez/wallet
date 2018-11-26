from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.config import config

import secrets
import random
from datetime import datetime, timedelta

import traceback

now = datetime.utcnow()
BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
WALLET_CONFIG          = config.Config.WALLET_CONFIG
TRANSACTION_NOTES      = config.Config.TRANSACTION_NOTES


class ApiKey(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), unique=True)
    label         = db.Column(db.String(120), unique=True)
    access_key    = db.Column(db.String(255), unique=True)
    name          = db.Column(db.String(100), unique=True)
    expiration    = db.Column(db.DateTime) #datetime
    created_at    = db.Column(db.DateTime, default=now)

    def __repr__(self):
        return '<ApiKey {}>'.format(self.access_key)
    #end def

    def generate_access_key(self, digit):
        self.access_key= secrets.token_hex(digit)
    #end def

    def set_expiration(self, expires_in):
        self.expiration = now + timedelta(minutes=int(expires_in)) # 1 year expiration
    #end def

    def revoke_access_key(self):
        self.expiration = now - timedelta(seconds=1)
    #end def

    @staticmethod
    def check_access_key(access_key):
        result = ApiKey.query.filter_by(access_key=access_key).first()
        if result is None or result.expiration < now:
            return None
        return result
    #end def

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #end def

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    #end def
#end class

class User(db.Model):
    id              = db.Column(db.BigInteger, primary_key=True)
    username        = db.Column(db.String(144), unique=True)
    name            = db.Column(db.String(144))
    msisdn          = db.Column(db.String(12), unique=True)
    email           = db.Column(db.String(144), unique=True)
    created_at      = db.Column(db.DateTime, default=now)
    password_hash   = db.Column(db.String(128))
    status          = db.Column(db.Boolean, default=True)
    role            = db.Column(db.Integer)
    wallets         = db.relationship("Wallet", back_populates="user", cascade="delete")

    def __repr__(self):
        return '<User {} {} {} {}>'.format(self.username,
                                     self.name, self.msisdn, self.email,
                                    )
    #end def

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #end def

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
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

class VirtualAccount(db.Model):
    id              = db.Column(db.BigInteger, primary_key=True)
    bank_id         = db.Column(db.Integer)
    va_type         = db.Column(db.Integer)
    trx_id          = db.Column(db.BigInteger, unique=True)
    trx_amount      = db.Column(db.Float, default=0)
    name            = db.Column(db.String(144))
    datetime_expired= db.Column(db.DateTime)
    status          = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=now)
    wallet_id       = db.Column(db.BigInteger, db.ForeignKey('wallet.id'))
    wallet          = db.relationship("Wallet", back_populates="virtual_accounts", cascade="delete")

    def __repr__(self):
        return '<VirtualAccount {} {} {} {}>'.format(self.id, self.trx_id, self.name, self.status)
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

    def generate_va_number(self, va_type):
        va_id = None
        while True:
            fixed = 988
            if va_type == "CREDIT":
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

    @staticmethod
    def inject_balance(va_source, wallet_id, amount):
        try:
            # fetch wallet object
            wallet = Wallet.query.filter_by(id=wallet_id).first()

            # create credit transaction
            credit_transaction = Transaction(
                    source_id=wallet_id,
                    destination_id=wallet_id,
                    amount=amount,
                    transaction_type=WALLET_CONFIG["CREDIT_FLAG"],
                    notes=TRANSACTION_NOTES["DEPOSIT"].format(str(amount))
            )
            credit_transaction.generate_trx_id()
            db.session.add(credit_transaction)
            wallet.add_balance(amount)
            db.session.commit()
        except:
            print(traceback.format_exc())
            return False
        return True
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
    token       = db.Column(db.String(120))
    created_at  = db.Column(db.DateTime, default=now)

    @staticmethod
    def is_blacklisted(token):
        result = BlacklistToken.query.filter_by(token=token).first()
        return bool(result)

    def __repr__(self):
        return '<Blacklist Token {} {}>'.format(self.id, self.jti)
    #end def
#end class

