import re

from marshmallow import fields, ValidationError, post_load, validates

from app         import ma,db
from app.models  import ApiKey, Wallet, Transaction, VirtualAccount, User
from app.config  import config

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
WALLET_CONFIG          = config.Config.WALLET_CONFIG

def cannot_be_blank(string):
    if not string:
        raise ValidationError(" Data cannot be blank")
#end def

class ApiKeySchema(ma.Schema):

    username   = fields.Str(required=True, validate=cannot_be_blank)
    password   = fields.Str(required=True, attribute="password_hash", validate=cannot_be_blank)
    label      = fields.Str(required=True, validate=cannot_be_blank)
    name       = fields.Str(required=True, validate=cannot_be_blank)
    expiration = fields.Int(required=True)
    id         = fields.Int()
    access_key = fields.Str()

    class Meta:
        #strict = True
        pass

    @validates('expiration')
    def validate_expiration(self, expiration):
        if expiration <= 0:
            raise ValidationError('Invalid Expiration, Cannot be less or equal 0')
    #end def

    @post_load
    def make_api_key(self, data):
        return ApiKey(**data)
    #end def
#end class

class UserSchema(ma.Schema):
    id         = fields.Int()
    username   = fields.Str(required=True, validate=cannot_be_blank)
    name       = fields.Str(required=True, validate=cannot_be_blank)
    msisdn     = fields.Str(required=True, validate=cannot_be_blank)
    email      = fields.Str(required=True, validate=cannot_be_blank)
    password   = fields.Str(required=True, attribute="password_hash", validate=cannot_be_blank, load_only=True)
    created_at = fields.Date()
    status     = fields.Bool()

    class Meta():
        pass
        #strict = True

    @post_load
    def make_user(self, data):
        return User(**data)
    #end def

    @validates('msisdn')
    def validate_msisdn(self, msisdn):
        msisdn_length = len(msisdn)
        if 11 <= msisdn_length <= 12:
            if re.search(r'^[-+]?[0-9]+$', msisdn) != None:
               pass
        else:
            raise ValidationError('Invalid phone number')
    #end def

    @validates('email')
    def validate_email(self, email):
        if re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) != None:
            pass
        else:
            raise ValidationError('Invalid email')
    #end def

    @validates('password')
    def validate_password(self, password):
        if re.match(r'[A-Za-z0-9@#$%^&+=]{6,}', password):
            pass
        else:
            raise ValidationError("Invalid Password, Minimum 6 Character")
    #end def
#end class

class WalletSchema(ma.Schema):
    id         = fields.Int()
    user_id    = fields.Int()
    pin        = fields.Str(required=True, attribute="pin_hash", validate=cannot_be_blank, load_only=True)
    created_at = fields.Date()
    status     = fields.Bool()
    balance    = fields.Float()

    class Meta():
        pass
        #strict = True

    @post_load
    def make_wallet(self, data):
        return Wallet(**data)
    #end def

    @validates('pin')
    def validate_pin(self, pin):
        if re.fullmatch("\d{4}|\d{6}", pin):
            pass
        else:
            raise ValidationError("Invalid Pin, Minimum 4-6 digit")
    #end def

#end class

class TransactionSchema(ma.Schema):
    id               = fields.Int()
    source_id        = fields.Int()
    destination_id   = fields.Int()
    amount           = fields.Float()
    transaction_type = fields.Int()
    transfer_type    = fields.Int()
    notes            = fields.Str()
    created_at       = fields.Date()

    @validates('amount')
    def validate_amount(self, amount):
        if float(amount) <= 0:
            raise ValidationError("Invalid Amount, cannot be less than 0")
    #end def


class VirtualAccountSchema(ma.Schema):
    id         = fields.Int()
    trx_id     = fields.Int()
    name       = fields.Str(required=True, validate=cannot_be_blank)
    #wallet_id  = fields.Int(required=True)
    status     = fields.Bool()

    @post_load
    def make_wallet(self, data):
        return VirtualAccount(**data)
    #end def
#end class

class CallbackSchema(ma.Schema):
    virtual_account           = fields.Int(required=True, validate=cannot_be_blank)
    customer_name             = fields.Str(required=True, validate=cannot_be_blank)
    trx_id                    = fields.Int(required=True, validate=cannot_be_blank)
    trx_amount                = fields.Float(required=True)
    payment_amount            = fields.Int(required=True, validate=cannot_be_blank)
    cumulative_payment_amount = fields.Int(required=True, validate=cannot_be_blank)
    payment_ntb               = fields.Int(required=True, validate=cannot_be_blank)
    datetime_payment          = fields.Str(required=True, validate=cannot_be_blank)

    @validates('virtual_account')
    def validate_va_number(self, va_number):
        va_number = str(va_number)
        valid = True
        # first make sure va_number is 16 digit can't be less or more
        if len(va_number) != 16:
            # second make sure 3 first va_number is valid
            if va_number[:3] != "988":
                # third make sure 3 first va_number is valid
                if va_number[3:8] != BNI_ECOLLECTION_CONFIG["CLIENT_ID"]:
                    valid = False
                #end if
                valid = False
            #end if
            valid = False
        #end if

        if valid == False:
            raise ValidationError("Invalid Virtual Account Number")
        #end if

    @validates('payment_amount')
    def validate_payment_amount(self, payment_amount):
        if payment_amount < WALLET_CONFIG["MINIMAL_DEPOSIT"]:
            raise ValidationError("Minimal deposit is {}".format(str(WALLET_CONFIG["MINIMAL_DEPOSIT"])))
        #end if

        if payment_amount > WALLET_CONFIG["MAX_DEPOSIT"]:
            raise ValidationError("Maximum deposit is {}".format(str(WALLET_CONFIG["MAX_DEPOSIT"])))
        #end if
    #end def

#end class
