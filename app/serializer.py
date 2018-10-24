from app         import ma,db
from app.models  import ApiKey, Wallet, Transaction

from marshmallow import fields, ValidationError, post_load, validates

import re

def cannot_be_blank(string):
    if not string:
        raise ValidationError(" Data cannot be blank")
#end def

class ApiKeySchema(ma.Schema):

    label      = fields.Str(required=True, validate=cannot_be_blank)
    name       = fields.Str(required=True, validate=cannot_be_blank)
    expiration = fields.Int(required=True)
    id         = fields.Int()
    access_key = fields.Str()

    class Meta:
        #strict = True
        pass

    @post_load
    def make_api_key(self, data):
        return ApiKey(**data)
    #end def
#end class

class WalletSchema(ma.Schema):
    id         = fields.Int()
    name       = fields.Str(required=True, validate=cannot_be_blank)
    msisdn     = fields.Str(required=True, validate=cannot_be_blank)
    email      = fields.Str(required=True, validate=cannot_be_blank)
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

    @validates('pin')
    def validate_pin(self, pin):
        if re.fullmatch("\d{4}|\d{6}", pin):
            pass
        else:
            raise ValidationError("Invalid Pin, Minimum 4-6 digit")
    #end def

#end class

class TransactionSchema(ma.ModelSchema):
    class Meta:
        model = Transaction

    @validates('amount')
    def validate_amount(self, amount):
        if amount < 0:
            raise ValidationError("Invalid Amount, cannot be less than 0")
