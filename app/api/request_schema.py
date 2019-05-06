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
    parser.add_argument("email",       type=str)
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
    parser.add_argument("email",       type=str)
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

class PinOnlyRequestSchema:
    """Define all mandatory argument for verify pin"""
    parser = reqparse.RequestParser()
    parser.add_argument("pin", type=str, required=True)
#end class

class TransferRequestSchema:
    """Define all mandatory argument for wallet transfer"""
    parser = reqparse.RequestParser()
    parser.add_argument("amount", type=int, required=True)
    parser.add_argument("pin",    type=str, required=True)
    parser.add_argument("notes",  type=str)
    parser.add_argument("types",  type=str)
#end class

class TransferCheckoutRequestSchema:
    """Define all mandatory argument for transfer checkout"""
    parser = reqparse.RequestParser()
    parser.add_argument("phone_ext",   type=str, required=True)
    parser.add_argument("phone_number",type=str, required=True)
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

class PaymentPlanRequestSchema:
    """Define all mandatory argument for creating Payment Plan """
    parser = reqparse.RequestParser()
    parser.add_argument("id", type=str)
    parser.add_argument("destination", type=str, required=True)
    parser.add_argument("wallet_id", type=str, required=True)
    parser.add_argument("method", type=str)
    parser.add_argument("plans", type=dict, action='append')
    parser.add_argument("status", type=str)
#end class

class PlanRequestSchema:
    """Define all mandatory argument for creating Payment Plan """
    parser = reqparse.RequestParser()
    parser.add_argument("id", type=str)
    parser.add_argument("payment_plan_id", type=str, required=True)
    parser.add_argument("amount", type=int, required=True)
    parser.add_argument("type", type=str, required=True)
    parser.add_argument("due_date", type=str, required=True)
#end class

class UpdatePlanRequestSchema:
    """Define all mandatory argument for updating Payment Plan """
    parser = reqparse.RequestParser()
    parser.add_argument("status", type=str, required=True)
#end class

class BNIUtilityRequestSchema:
    """Define all mandatory argument for BNI utility """
    parser = reqparse.RequestParser()
    parser.add_argument("account_no", type=str, required=True)
    parser.add_argument("amount", type=int, required=True)
#end class

class BNIUtilityDoPaymentRequestSchema:
    """Define all mandatory argument for BNI Do Payment"""
    parser = reqparse.RequestParser()
    parser.add_argument("method", type=str, required=True)
    parser.add_argument("source_account", type=str, required=True)
    parser.add_argument("account_no", type=str, required=True)
    parser.add_argument("amount", type=str, required=True)
    parser.add_argument("email", type=str, required=True)
    parser.add_argument("clearing_code", type=str, required=True)
    parser.add_argument("account_name", type=str, required=True)
    parser.add_argument("address", type=str, required=True)
    parser.add_argument("charge_mode", type=str, required=True)
    parser.add_argument("ref_number", type=str)
#end class

class BNIUtilityInterbankInquiryRequestSchema:
    """Define all mandatory argument for BNI Do Payment"""
    parser = reqparse.RequestParser()
    parser.add_argument("source_account", location='args', type=str, required=True)
    parser.add_argument("bank_code", location='args', type=str, required=True)
    parser.add_argument("account_no", location='args', type=str, required=True)
    parser.add_argument("ref_number", location='args', type=str)
#end class

class BNIUtilityInterbankPaymentRequestSchema:
    """Define all mandatory argument for BNI Do Payment"""
    parser = reqparse.RequestParser()
    parser.add_argument("source_account", type=str, required=True)
    parser.add_argument("account_no", type=str, required=True)
    parser.add_argument("account_name", type=str, required=True)
    parser.add_argument("bank_code", type=str, required=True)
    parser.add_argument("bank_name", type=str, required=True)
    parser.add_argument("amount", type=str, required=True)
    parser.add_argument("transfer_ref", type=str, required=True)
    parser.add_argument("ref_number", type=str)
#end class

class QRTransferRequestSchema:
    """Define all mandatory argument for qr transfer """
    parser = reqparse.RequestParser()
    parser.add_argument("qr_string", type=str, required=True)
#end class
