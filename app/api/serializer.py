import re

from marshmallow import fields, ValidationError, post_load, validates

from app.api         import ma, db
from app.api.models  import Wallet, Transaction, VirtualAccount, User, Role
from app.api.config  import config

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
WALLET_CONFIG          = config.Config.WALLET_CONFIG

def cannot_be_blank(string):
    if not string:
        raise ValidationError(" Data cannot be blank")
#end def

class BankSchema(ma.Schema):
    id   = fields.Int(load_only=True)
    name = fields.Str(required=True, validate=cannot_be_blank)
    code = fields.Str(required=True, validate=cannot_be_blank)

class BankAccountSchema(ma.Schema):
    id         = fields.Int()
    name       = fields.Str(required=True, validate=cannot_be_blank)
    account_no = fields.Str(required=True, validate=cannot_be_blank)
    label      = fields.Str(required=True, validate=cannot_be_blank)
    bank_code  = fields.Str(required=True, validate=cannot_be_blank, load_only=True)
    bank_name  = fields.Method("bank_id_to_name")

    def bank_id_to_name(self, obj):
        return obj.bank.name
    #end def

    @validates('name')
    def validate_name(self, name):
        # onyl allow alphabet space character
        pattern = r"^[a-zA-Z ]+$"
        if len(name) < 2:
            raise ValidationError('Invalid name, minimum is 2 character')
        if len(name) > 35:
            raise ValidationError('Invalid name, max is 35 character')
        if  re.match(pattern, name) is None:
            raise ValidationError('Invalid name, only alphabet allowed')
    #end def

    @validates('label')
    def validate_label(self, label):
        # onyl allow alphabet character and space
        pattern = r"^[a-zA-Z ]+$"
        if len(label) < 2:
            raise ValidationError('Invalid label, minimum is 2 character')
        if len(label) > 30:
            raise ValidationError('Invalid label, max is 30 character')
        if  re.match(pattern, label) is None:
            raise ValidationError('Invalid label, only alphabet allowed')
    #end def

    @validates('account_no')
    def validate_account_no(self, account_no):
        # only allow 0-9, minimal 10 and maximal is 16 digit
        pattern = r"^[0-9]{10,16}$"
        if re.search(pattern, account_no) is None:
            raise ValidationError('Invalid account number, only number allowed')
        elif int(account_no) < 1:
            raise ValidationError("account no can't be 0")
        #end if
    #end def

    @validates('bank_code')
    def validate_bank_code(self, bank_code):
        pattern = r"^[0-9]{1,3}$"
        if re.search(pattern, bank_code) is None:
            raise ValidationError('Invalid bank code, only number allowed')
        elif int(bank_code) < 1:
            raise ValidationError("bank code can't be 0")
        #end if
    #end def
#end def

class UserSchema(ma.Schema):
    id          = fields.Int(load_only=True)
    username    = fields.Str(required=True, validate=cannot_be_blank)
    name        = fields.Str(required=True, validate=cannot_be_blank)
    phone_ext   = fields.Str(required=True, validate=cannot_be_blank, load_only=True)
    phone_number= fields.Str(required=True, validate=cannot_be_blank, load_only=True)
    msisdn      = fields.Method("phone_to_msisdn", dump_only=True)
    email       = fields.Str(required=True, validate=cannot_be_blank)
    role        = fields.Method("role_id_to_role", validate=cannot_be_blank)
    password    = fields.Str(required=True, attribute="password_hash", validate=cannot_be_blank, load_only=True)
    pin         = fields.Str(required=True, validate=cannot_be_blank, load_only=True)
    created_at  = fields.DateTime('%Y-%m-%d %H:%M:%S')
    status      = fields.Method("bool_to_status")

    class Meta():
        pass

    def phone_to_msisdn(self, obj):
        return obj.phone_ext + obj.phone_number
    #end def

    def bool_to_status(self, obj):
        status = "ACTIVE"
        if obj.status != True:
            status = "INACTIVE"
        return status
    #end def

    def role_id_to_role(self, obj):
        return obj.role.description
    #end def

    @post_load
    def make_user(self, data):
        return User(**data)
    #end def

    @validates('username')
    def validate_username(self, username):
        # onyl allow alphanumeric character, . _ -
        pattern = r"^[a-zA-Z0-9_.-]+$"
        if len(username) < 5:
            raise ValidationError('Invalid username, minimum is 5 character')
        if len(username) > 32:
            raise ValidationError('Invalid username, max is 32 character')
        if  re.match(pattern, username) is None:
            raise ValidationError('Invalid username, only alphanumeric, . _ - allowed')
    #end def

    @validates('name')
    def validate_name(self, name):
        # onyl allow alphabet character
        pattern = r"^[a-zA-Z ]+$"
        if len(name) < 2:
            raise ValidationError('Invalid name, minimum is 2 character')
        if len(name) > 70:
            raise ValidationError('Invalid name, max is 70 character')
        if  re.match(pattern, name) is None:
            raise ValidationError('Invalid name, only alphabet allowed')
    #end def

    @validates('phone_ext')
    def validate_phone_ext(self, phone_ext):
        # only allow 0-9, minimal 1 and maximal is 3 digit
        pattern = r"^[0-9]{1,3}$"
        if re.search(pattern, phone_ext) is None:
            raise ValidationError('Invalid phone ext, only number allowed')
        elif int(phone_ext) < 1:
            raise ValidationError("phone ext can't be 0")
        #end if
    #end def

    @validates('phone_number')
    def validate_phone_number(self, phone_number):
        # only allow 0-9, minimal 9 and maximal is 11 digit
        pattern = r"^[0-9]{9,11}$"
        if re.search(pattern, phone_number) is None:
            raise ValidationError('Invalid phone number, only number allowed')
        elif int(phone_number) < 1:
            raise ValidationError("phone number can't be 0")
        #end if
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

    @validates('role')
    def validate_role(self, role):
        pattern = r"^[a-zA-Z]+$"
        if re.match(pattern, role) is None:
            raise ValidationError("Invalid Role, only alphabet allowed")
        #end if

        if role not in ["ADMIN", "USER"]:
            raise ValidationError("Invalid Role")
    #end def

    @validates('pin')
    def validate_pin(self, pin):
        if re.match(r"\d{6}", pin):
            pass
        else:
            raise ValidationError("Invalid Pin, Minimum 6 digit")
    #end def
#end class

class WalletSchema(ma.Schema):
    id         = fields.Int()
    user_id    = fields.Int(load_only=True)
    pin        = fields.Str(required=True, attribute="pin_hash", validate=cannot_be_blank, load_only=True)
    created_at = fields.DateTime('%Y-%m-%d %H:%M:%S', load_only=True)
    status     = fields.Method("bool_to_status")
    balance    = fields.Float()

    class Meta():
        pass
        #strict = True

    def bool_to_status(self, obj):
        status = "ACTIVE"
        if obj.status != True:
            status = "INACTIVE"
        return status
    #end def

    @post_load
    def make_wallet(self, data):
        return Wallet(**data)
    #end def

    @validates('pin')
    def validate_pin(self, pin):
        if re.match(r"\d{6}", pin):
            pass
        else:
            raise ValidationError("Invalid Pin")
    #end def

#end class

class TransactionSchema(ma.Schema):
    id               = fields.Int()
    wallet_id        = fields.Int()
    balance          = fields.Float()
    amount           = fields.Float()
    transaction_type = fields.Int()
    notes            = fields.Str()
    payment_id       = fields.Method("payment_id_to_details")
    created_at       = fields.DateTime('%Y-%m-%d %H:%M:%S')

    @validates('amount')
    def validate_amount(self, amount):
        if float(amount) <= 0:
            raise ValidationError("Invalid Amount, cannot be less than 0")
    #end def

    def payment_id_to_details(self, obj):
        payment_details = {
            "source"          : obj.payment.source_account,
            "to"              : obj.payment.to,
            "reference_number": obj.payment.ref_number,
            "amount"          : obj.payment.amount,
            "payment_type"    : obj.payment.payment_type,
            "status"          : obj.payment.status,
        }
        return payment_details
    #end def
#end class

class VirtualAccountSchema(ma.Schema):
    id         = fields.Int()
    trx_id     = fields.Int(load_only=True)
    va_type    = fields.Method("va_type_to_string")
    name       = fields.Str(required=True, validate=cannot_be_blank)
    status     = fields.Method("bool_to_status")

    @post_load
    def make_wallet(self, data):
        return VirtualAccount(**data)
    #end def

    def bool_to_status(self, obj):
        status = "ACTIVE"
        if obj.status != True:
            status = "INACTIVE"
        return status
    #end def

    def va_type_to_string(self, obj):
        return obj.va_type.key
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
                if va_number[3:8] != BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"] or va_number[3:8] != BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"]:
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
        # if payment amount is positive it means deposit
        if payment_amount > 0:
            if payment_amount < WALLET_CONFIG["MINIMAL_DEPOSIT"]:
                raise ValidationError("Minimal deposit is {}".format(str(WALLET_CONFIG["MINIMAL_DEPOSIT"])))
            #end if

            if payment_amount > WALLET_CONFIG["MAX_DEPOSIT"]:
                raise ValidationError("Maximum deposit is {}".format(str(WALLET_CONFIG["MAX_DEPOSIT"])))
            #end if
        # negatives it means withdraw
        elif payment_amount < 0:
            if abs(payment_amount) < WALLET_CONFIG["MINIMAL_WITHDRAW"]:
                raise ValidationError("Minimal withdraw is {}".format(str(WALLET_CONFIG["MINIMAL_WITHDRAW"])))
            #end if

            if abs(payment_amount) > WALLET_CONFIG["MAX_WITHDRAW"]:
                raise ValidationError("Maximum withdraw is {}".format(str(WALLET_CONFIG["MAX_WITHDRAW"])))
            #end if
        #end if
#end class
