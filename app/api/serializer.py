"""
    Serializer
    _______________
    this is module to serialize and deserialize object
"""
# pylint: disable=R0201

import re
from datetime import datetime
from marshmallow import fields, ValidationError, post_load, validates

from app.api         import ma
from app.api.models  import *
from app.config  import config

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
WALLET_CONFIG = config.Config.WALLET_CONFIG
TRANSACTION_CONFIG = config.Config.TRANSACTION_CONFIG

def cannot_be_blank(string):
    """
        function to make user not enter empty string
        args :
            string -- user inputted data
    """
    if not string:
        raise ValidationError(" Data cannot be blank")
#end def

class BankSchema(ma.Schema):
    """
        This is Class Schema for Bank Object
    """
    id   = fields.Int(load_only=True)
    name = fields.Str(required=True, validate=cannot_be_blank)
    code = fields.Str(required=True, validate=cannot_be_blank)

class BankAccountSchema(ma.Schema):
    """
        This is Class Schema for Bank Account Object
    """
    id         = fields.Int()
    name       = fields.Str(required=True, validate=cannot_be_blank)
    account_no = fields.Str(required=True, validate=cannot_be_blank)
    label      = fields.Str(required=True, validate=cannot_be_blank)
    bank_code  = fields.Str(required=True, validate=cannot_be_blank, load_only=True)
    bank_name  = fields.Method("bank_id_to_name")

    def bank_id_to_name(self, obj):
        """ 
            function to convert bank id to bank name
            args : 
                obj -- bank account object
        """
        return obj.bank.name
    #end def

    @validates('name')
    def validate_name(self, name):
        """
            function to validate name field
            args :
                name -- bank account name
        """
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
        """
            function to validate label field
            args :
                label -- bank account label
        """
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
        """
            function to validate account_no field
            args :
                account_no -- bank account no
        """
        # only allow 0-9, minimal 10 and maximal is 16 digit
        pattern = r"^[0-9]{10,30}$"
        if re.search(pattern, account_no) is None:
            raise ValidationError('Invalid account number, only number allowed')
        elif int(account_no) < 1:
            raise ValidationError("account no can't be 0")
        #end if
    #end def

    @validates('bank_code')
    def validate_bank_code(self, bank_code):
        """
            function to validate bank_code field
            args :
                bank_code -- bank code
        """
        pattern = r"^[0-9]{1,3}$"
        if re.search(pattern, bank_code) is None:
            raise ValidationError('Invalid bank code, only number allowed')
        elif int(bank_code) < 1:
            raise ValidationError("bank code can't be 0")
        #end if
    #end def

    @post_load
    def make_object(self, request_data):
        del request_data["bank_code"]
        return BankAccount(**request_data)

#end def

class UserSchema(ma.Schema):
    """ this is class schema for user object"""
    id          = fields.Str()
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

    def phone_to_msisdn(self, obj):
        """
            function to convert phone_ext and phone_number into msisdn
            args:
                obj - user object
        """
        return obj.phone_ext + obj.phone_number
    #end def

    def bool_to_status(self, obj):
        """
            function to convert boolean into human friendly string
            args:
                obj - user object
        """
        status = "ACTIVE"
        if obj.status == 2:
            status = "DEACTIVE"
        elif obj.status == 3:
            status = "LOCKED"
        return status
    #end def

    def role_id_to_role(self, obj):
        """
            function to convert role id into human friendly string
            args:
                obj - user object
        """
        return obj.role.description
    #end def

    @post_load
    def make_user(self, data):
        """ create user object from data"""
        role = Role.query.filter_by(description=data["role"]).first()
        del data["role"]
        data["role_id"] = role.id
        # remove pin and password
        del data["pin"]
        del data["password_hash"]

        return User(**data)
    #end def

    @validates('username')
    def validate_username(self, username):
        """
            function to validate username
            args:
                username -- username
        """
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
        """
            function to validate name
            args:
                name -- name
        """
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
        """
            function to validate phone_ext
            args:
                phone_ext -- phone extension
        """
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
        """
            function to validate phone_number
            args:
                phone_number -- phone number
        """
        # only allow 0-9, minimal 9 and maximal is 14 digit
        pattern = r"^[0-9]{9,14}$"
        if re.search(pattern, phone_number) is None:
            raise ValidationError('Invalid phone number, only number allowed')
        elif int(phone_number) < 1:
            raise ValidationError("phone number can't be 0")
        #end if
    #end def

    @validates('email')
    def validate_email(self, email):
        """
            function to validate email
            args:
                email -- email
        """
        if re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) != None:
            pass
        else:
            raise ValidationError('Invalid email')
    #end def

    @validates('password')
    def validate_password(self, password):
        """
            function to validate password
            args:
                password -- password
        """
        if re.match(r'[A-Za-z0-9@#$%^&+=]{6,}', password):
            pass
        else:
            raise ValidationError("Invalid Password, Minimum 6 Character")
    #end def

    @validates('role')
    def validate_role(self, role):
        """
            function to validate role
            args:
                role -- role
        """
        pattern = r"^[a-zA-Z]+$"
        if re.match(pattern, role) is None:
            raise ValidationError("Invalid Role, only alphabet allowed")
        #end if

        if role not in ["ADMIN", "USER"]:
            raise ValidationError("Invalid Role")
    #end def

    @validates('pin')
    def validate_pin(self, pin):
        """
            function to validate pin
            args:
                pin -- pin
        """
        if re.match(r"\d{6}", pin):
            pass
        else:
            raise ValidationError("Invalid Pin, Minimum 6 digit")
    #end def
#end class

class WalletSchema(ma.Schema):
    """ This is class that represent wallet schema"""
    id         = fields.Str()
    label      = fields.Str(required=True, load_only=True, validate=cannot_be_blank)
    user_id    = fields.Int(load_only=True)
    pin        = fields.Str(required=True, attribute="pin_hash", validate=cannot_be_blank, load_only=True)
    created_at = fields.DateTime('%Y-%m-%d %H:%M:%S', load_only=True)
    status     = fields.Method("bool_to_status")
    balance    = fields.Float()

    def bool_to_status(self, obj):
        """
            funtion to convert boolean to human friendly string
            args:
                obj -- wallet object
        """
        status = "ACTIVE"
        if obj.status == 0:
            status = "INACTIVE"
        elif obj.status == 2:
            status = "LOCKED"
        return status
    #end def

    @post_load
    def make_wallet(self, data):
        return Wallet(**data)
    #end def

    @validates('label')
    def validate_label(self, name):
        """
            function to validate wallet label
            args:
                name -- name
        """
        # onyl allow alphabet character
        pattern = r"^[a-zA-Z ]+$"
        if len(name) < 2:
            raise ValidationError('Invalid label, minimum is 2 character')
        if len(name) > 70:
            raise ValidationError('Invalid label, max is 100 character')
        if  re.match(pattern, name) is None:
            raise ValidationError('Invalid label, only alphabet allowed')
    #end def

    @validates('pin')
    def validate_pin(self, pin):
        """
        function to validate pin
            args:
                pin -- user pin
        """
        if re.match(r"\d{6}", pin):
            pass
        else:
            raise ValidationError("Invalid Pin")
    #end def

#end class

class WithdrawSchema(ma.Schema):
    """ This is class that represent Withdraw Schema"""
    amount = fields.Float()
    pin = fields.Str(required=True, attribute="pin_hash", validate=cannot_be_blank, load_only=True)

    @validates('amount')
    def validate_amount(self, amount):
        """
            Function to validate transaction amount
            args :
                amount -- Transaction amount
        """
        if float(amount) < 0:
            raise ValidationError("Invalid Amount, cannot be less than 0")
    #end def

    @validates('pin')
    def validate_pin(self, pin):
        """
        function to validate pin
            args:
                pin -- user pin
        """
        if re.match(r"\d{6}", pin):
            pass
        else:
            raise ValidationError("Invalid Pin")
    #end def
#end class

class TransactionSchema(ma.Schema):
    """ This is class that represent Transaction Schema"""
    id               = fields.Str()
    wallet_id        = fields.Str()
    balance          = fields.Float()
    amount           = fields.Float()
    transaction_type = fields.Method("transaction_type_id_to_string")
    notes            = fields.Str(allow_none=True)
    payment_details  = fields.Method("payment_id_to_details")
    created_at       = fields.DateTime('%Y-%m-%d %H:%M:%S')

    @validates('notes')
    def validate_notes(self, notes):
        """
            function to validate transfer notes
            args :
                transfer notes
        """
        # onyl allow alphabet character and space
        if notes is not None:
            pattern = r"^[a-zA-Z ]+$"
            if len(notes) < 4:
                raise ValidationError('Invalid notes, minimum is 4 character')
            if len(notes) > 50:
                raise ValidationError('Invalid notes, max is 50 character')
            if  re.match(pattern, notes) is None:
                raise ValidationError('Invalid notes, only alphabet allowed')
    #end def

    @validates('amount')
    def validate_amount(self, amount):
        """
            Function to validate transaction amount
            args :
                amount -- Transaction amount
        """
        if float(amount) <= 0:
            raise ValidationError("Invalid Amount, cannot be less than 0")
    #end def

    def payment_id_to_details(self, obj):
        """
            Function to convert payment id to readable payment details
            args :
                obj -- payment object
        """
        payment_details = {
            "source"          : obj.payment.source_account,
            "to"              : obj.payment.to,
            "reference_number": obj.payment.ref_number,
            "payment_amount"  : obj.payment.amount,
            "payment_type"    : self.payment_type_to_string(obj.payment.payment_type),
            "status"          : self.payment_status_to_string(obj.payment.status),
        }
        return payment_details
    #end def

    def transaction_type_id_to_string(self, obj):
        """
            Function to convert transaction type id to readable transaction
            type
            args :
                obj -- payment object
        """
        result = ""
        if obj.transaction_type == 1:
            result = "DEPOSIT"
        elif obj.transaction_type == 2:
            result = "TOP_UP"
        elif obj.transaction_type == 3:
            result = "TRANSFER_IN"
        elif obj.transaction_type == 4:
            result = "TRANSFER_OUT"
        else:
            result = "RECEIVE_TRANSFER"
        return result
    #end def

    def payment_type_to_string(self, payment_type):
        """
            Function to convert transaction type id to readable transaction
            type
            args :
                payment_type -- Payment type
        """
        result = ""
        if payment_type:
            result = "CREDIT"
        else:
            result = "DEBIT"
        #end if
        return result
    #end def

    def payment_status_to_string(self, status):
        """
            Function to convert payment status to readable string
            args :
                status -- payment status
        """
        result = ""
        if status == 1:
            result = "COMPLETED"
        elif status == 2:
            result = "PENDING"
        elif status == 3:
            result = "FAILED"
        #end if
        return result
    #end def
#end class

class VirtualAccountSchema(ma.Schema):
    """ This is class for Virtual Account Schema"""
    account_no = fields.Str()
    trx_id     = fields.Int(load_only=True)
    va_type    = fields.Method("va_type_to_string")
    name       = fields.Str(required=True, validate=cannot_be_blank)
    bank_name  = fields.Method("bank_id_to_name")
    status     = fields.Method("bool_to_status")

    @post_load
    def make_va(self, data):
        """
            To make va object from data
            args:
                data -- data
        """
        return VirtualAccount(**data)
    #end def

    def bool_to_status(self, obj):
        """
            function to convert bool to human friendly status
            args:
                object -- va object
        """
        status = "ACTIVE"
        if obj.status == 0:
            status = "PENDING"
        elif obj.status == 2:
            status = "DEACTIVE"
        elif obj.status == 3:
            status = "LOCKED"
        return status
    #end def

    def bank_id_to_name(self, obj):
        """ 
            function to convert bank id to bank name
            args : 
                obj -- bank account object
        """
        return obj.bank.name
    #end def

    def va_type_to_string(self, obj):
        """ function to convert va type to string"""
        return obj.va_type.key
    #end def
#end class

class CallbackSchema(ma.Schema):
    """ this is schema for callback object """
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
        """
            function to validate virtual_account number
            args:
                va_number -- virtual account number
        """
        va_number = str(va_number)
        valid = True
        # first make sure va_number is 16 digit can't be less or more
        if len(va_number) != 16:
            # second make sure 3 first va_number is valid
            if va_number[:3] != "988":
                # third make sure 3 first va_number is valid
                if va_number[3:8] != BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"]\
                or va_number[3:8] != BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"]:
                    valid = False
                #end if
                valid = False
            #end if
            valid = False
        #end if

        if valid is not True:
            raise ValidationError("Invalid Virtual Account Number")
        #end if

    @validates('payment_amount')
    def validate_payment_amount(self, payment_amount):
        """
            function to validate virtual account payment amount
            args:
                payment_amount -- Payment amount
        """
        # if payment amount is positive it means deposit
        if payment_amount > 0:
            if payment_amount < WALLET_CONFIG["MINIMAL_DEPOSIT"]:
                raise ValidationError("Minimal deposit is {}".
                                      format(str(WALLET_CONFIG["MINIMAL_DEPOSIT"])))
            #end if

            if payment_amount > WALLET_CONFIG["MAX_DEPOSIT"]:
                raise ValidationError("Maximum deposit is {}".
                                      format(str(WALLET_CONFIG["MAX_DEPOSIT"])))
            #end if
        # negatives it means withdraw
        elif payment_amount < 0:
            if abs(payment_amount) < WALLET_CONFIG["MINIMAL_WITHDRAW"]:
                raise ValidationError("Minimal withdraw is {}".
                                      format(str(WALLET_CONFIG["MINIMAL_WITHDRAW"])))
            #end if

            if abs(payment_amount) > WALLET_CONFIG["MAX_WITHDRAW"]:
                raise ValidationError("Maximum withdraw is {}".
                                      format(str(WALLET_CONFIG["MAX_WITHDRAW"])))
            #end if
        #end if
#end class

class ExternalLogSchema(ma.Schema):
    """ this is schema for external log object """
    id         = fields.Int(dump_only=True)
    status     = fields.Method("bool_to_status", dump_only=True)
    resource   = fields.Str(dump_only=True)
    api_name   = fields.Str(dump_only=True)
    request    = fields.Str(dump_only=True)
    response   = fields.Str(dump_only=True)
    api_type   = fields.Method("api_type_to_type", dump_only=True)
    created_at = fields.DateTime('%Y-%m-%d %H:%M:%S')
    response_time = fields.Float(dump_only=True)

    def bool_to_status(self, obj):
        """
            function to convert boolean into human friendly string
            args:
                obj - user object
        """
        status = "SUCCESS"
        if obj.status is not True:
            status = "FAILED"
        return status
    #end def

    def api_type_to_type(self, obj):
        """
            function to convert api tpye into human friendly string
            args:
                obj - user object
        """
        api_type = "OUTGOING"
        if obj.api_type == 1:
            api_type = "INCOMING"
        return api_type
    #end def

class WalletTransactionSchema(ma.Schema):
    """ this is schema for transaction log object """
    flag = fields.Str(load_only=True)
    start_date = fields.Str(load_only=True)
    end_date = fields.Str(load_only=True)

    @validates('flag')
    def validate_flag(self, flag):
        """
            function to validate transaction_type
            args:
                transaction_type -- Transaction type
        """
        if flag not in ["ALL", "IN", "OUT"]:
            raise ValidationError('Invalid transaction type')
    #end def

    @validates('start_date')
    def validate_start_date(self, start_date):
        """
            function to validate start_date
            args:
                start_date -- start_date
        """
        try:
            start_date = datetime.strptime(start_date, "%Y/%m/%d")
        except ValueError:
            raise ValidationError('Invalid start date format')
    #end def

    @validates('end_date')
    def validate_end_date(self, end_date):
        """
            function to validate end_date
            args:
                end_date -- End Date
        """
        try:
            end_date = datetime.strptime(end_date, "%Y/%m/%d")
        except ValueError:
            raise ValidationError('Invalid end date format')
    #end def
#end class
