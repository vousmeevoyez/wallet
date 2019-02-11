"""
    REQUEST SCHEMA
"""
#pylint: disable=too-few-public-methods
#pylint: disable=bad-whitespace
#pylint: disable=import-error

from flask_restplus import reqparse

class UserRequestSchema:
    """Define all mandatory argument for creating User"""
    parser = reqparse.RequestParser()
    parser.add_argument("username",    type=str, required=True)
    parser.add_argument("name",        type=str, required=True)
    parser.add_argument("phone_ext",   type=str, required=True)
    parser.add_argument("phone_number",type=str, required=True)
    parser.add_argument("email",       type=str, required=True)
    parser.add_argument("password",    type=str, required=True)
    parser.add_argument("pin",         type=str, required=True)
    parser.add_argument("role",        type=str, required=True)
#end class

class UserUpdateRequestSchema:
    """Define all mandatory argument for updating User"""
    parser = reqparse.RequestParser()
    parser.add_argument("name",        type=str, required=True)
    parser.add_argument("phone_ext",   type=str, required=True)
    parser.add_argument("phone_number",type=str, required=True)
    parser.add_argument("email",       type=str, required=True)
    parser.add_argument("password",    type=str, required=True)
#end class

class BankAccountRequestSchema:
    """Define all mandatory argument for creating bank account"""
    parser = reqparse.RequestParser()
    parser.add_argument("account_no",type=str, required=True)
    parser.add_argument("name",      type=str, required=True)
    parser.add_argument("label",     type=str, required=True)
    parser.add_argument("bank_code", type=str, required=True)
#end class

class AuthRequestSchema:
    """Define all mandatory argument for authentication"""
    parser = reqparse.RequestParser()
    parser.add_argument("username", type=str, required=True)
    parser.add_argument("password", type=str, required=True)
#end class

class WalletRequestSchema:
    """Define all mandatory argument for creating wallet"""
    parser = reqparse.RequestParser()
    parser.add_argument("label", type=str, required=True)
    parser.add_argument("pin", type=str, required=True)
#end class

class WalletUpdatePinRequestSchema:
    """Define all mandatory argument for updating pin"""
    parser = reqparse.RequestParser()
    parser.add_argument("old_pin",    type=str, required=True)
    parser.add_argument("pin",        type=str, required=True)
    parser.add_argument("confirm_pin",type=str, required=True)
#end class

class ForgotPinRequestSchema:
    """Define all mandatory argument for forgot pin"""
    parser = reqparse.RequestParser()
    parser.add_argument("pin",     type=str, required=True)
    parser.add_argument("otp_code",type=str, required=True)
    parser.add_argument("otp_key", type=str, required=True)
#end class

class TransferRequestSchema:
    """Define all mandatory argument for wallet transfer"""
    parser = reqparse.RequestParser()
    parser.add_argument("amount", type=int, required=True)
    parser.add_argument("pin",    type=str, required=True)
    parser.add_argument("notes",  type=str)
#end class

class WithdrawRequestSchema:
    """Define all mandatory argument for withdraw"""
    parser = reqparse.RequestParser()
    parser.add_argument("amount", type=int)
    parser.add_argument("pin",    type=str, required=True)
#end class

class WalletTransactionRequestSchema:
    """Define all mandatory argument for transaction history"""
    parser = reqparse.RequestParser()
    parser.add_argument("flag", type=str, required=True, location="args")
    parser.add_argument("start_date", type=str, location="args")
    parser.add_argument("end_date", type=str, location="args")

class QRTransferRequestSchema:
    """Define all mandatory argument for qr transfer """
    parser = reqparse.RequestParser()
    parser.add_argument("qr_string", type=str, required=True)
    parser.add_argument("amount", type=int, required=True)
    parser.add_argument("pin",    type=str, required=True)
    parser.add_argument("notes",  type=str)
#end class
