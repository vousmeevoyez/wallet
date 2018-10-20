from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.config import config

import secrets
import random
from datetime import datetime, timedelta

now = datetime.utcnow()
BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

class ApiKey(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    label        = db.Column(db.String(120), unique=True)
    access_key   = db.Column(db.String(255), unique=True)
    name         = db.Column(db.String(100), unique=True)
    expiration   = db.Column(db.DateTime)

    def __repr__(self):
        return '<ApiKey {}>'.format(self.access_key)

    def generate_access_key(self, digit):
        self.access_key= secrets.token_hex(digit)

    def set_expiration(self, expires_in):
        self.expiration = now + timedelta(minutes=int(expires_in)) # 1 year expiration

    def revoke_access_key(self):
        self.expiration = now - timedelta(seconds=1)

    @staticmethod
    def check_access_key(access_key):
        result = ApiKey.query.filter_by(access_key=access_key).first()
        if result is None or result.expiration < now:
            return None
        return result

class Wallet(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(144))
    msisdn    = db.Column(db.Integer, unique=True)
    email     = db.Column(db.String(144), unique=True)
    create_at = db.Column(db.DateTime, default=now)
    pin_hash  = db.Column(db.String(128))
    status    = db.Column(db.Boolean, default=True)
    balance   = db.Column(db.Float, default=0)

    def __repr__(self):
        return '<Wallet {}>'.format(self.id)

    def check_balance(self):
        return self.balance

    def is_unlocked(self):
        return self.status

    def add_balance(self, amount):
        self.balance = self.balance + amount

    def deduct_balance(self, amount):
        self.balance = self.balance - amount

    def lock(self):
        self.status = False

    def unlock(self):
        if self.status != True:
            self.status = True

    def generate_wallet_id(self):
        wallet_id = None
        while True:
            wallet_id_prefix = 11
            wallet_id_suffix = random.randint(
                1000000000,
                9999999999
            )
            wallet_id = str(wallet_id_prefix) + str(wallet_id_suffix)
            result = Wallet.query.filter_by(id=wallet_id).first()
            if result == None:
                break
            #end if
        #end while
        return wallet_id
    #end def

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

class VirtualAccount(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    client_id       = db.Column(db.Integer)
    trx_id          = db.Column(db.Integer, unique=True)
    trx_amount      = db.Column(db.Float, unique=True)
    billing_type    = db.Column(db.String(1), unique=True)
    customer_name   = db.Column(db.String(144), unique=True)
    customer_email  = db.Column(db.String(144), unique=True)
    customer_phone  = db.Column(db.Integer, unique=True)
    virtual_account = db.Column(db.Integer, unique=True)
    datetime_expired= db.Column(db.DateTime)
    wallet_id       = db.Column

    def __repr__(self):
        return '<VirtualAccount {}>'.format(self.virtual_account)

    def generate_va_number(self):
        va_id = None
        while True:
            fixed = 988
            client_id = BNI_ECOLLECTION_CONFIG["CLIENT_ID"]
            suffix = random.randint(
                10000000,
                99999999
            )
            va_id = str(fixed) + str(client_id) + str(suffix)
            result = VirtualAccount.query.filter_by(virtual_account=va_id).first()
            if result == None:
                break
            #end if
        #end while
        return va_id
    #end def

    def generate_trx_id(self):
        trx_id = None
        while True:
            trx_id = str(random.randint(
                100000000,
                999999999
            ))
            result = VirtualAccount.query.filter_by(trx_id=trx_id).first()
            if result == None:
                break
            #end if
        #end while
        return trx_id
    #end def


class Transaction(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    source      = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    destination = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    balance     = db.Column(db.Float)
    notes       = db.Column(db.String(255))

    def __repr__(self):
        return '<Transaction {}>'.format(self.id)
