from flask_restplus import reqparse, inputs

class UserRequestSchema:
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

class BankAccountRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("account_no",type=str, required=True)
    parser.add_argument("name",      type=str, required=True)
    parser.add_argument("label",     type=str, required=True)
    parser.add_argument("bank_code", type=str, required=True)
#end class

class AuthRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("username", type=str, required=True)
    parser.add_argument("password", type=str, required=True)
#end class

class WalletRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("name",   type=str, required=True)
    parser.add_argument("msisdn", type=str, required=True)
    parser.add_argument("pin",    type=str, required=True)
#end class

class WalletUpdatePinRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("pin",        type=str, required=True)
    parser.add_argument("confirm_pin",type=str, required=True)
#end class

class PinAuthRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("pin",type=str, required=True)
#end class

class ForgotPinRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("pin",     type=str, required=True)
    parser.add_argument("otp_code",type=str, required=True)
    parser.add_argument("otp_key", type=str, required=True)
#end class

class TransferRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("amount", type=int, required=True)
    parser.add_argument("pin",    type=str, required=True)
    parser.add_argument("notes",  type=str, required=True)
#end class

class WithdrawRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("amount", type=int, required=True)
    parser.add_argument("pin",    type=str, required=True)
#end class

class WalletTransactionRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("flag", type=str, required=True, location="args")
    parser.add_argument("start_date", type=str, location="args")
    parser.add_argument("end_date", type=str, location="args")
