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

class AuthRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("username", type=str)
    parser.add_argument("password", type=str)
#end class

class WalletRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("name",   type=str)
    parser.add_argument("msisdn", type=str)
    parser.add_argument("pin",    type=str)
#end class

class TransferRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("amount", type=int)
    parser.add_argument("pin",    type=str)
    parser.add_argument("notes",  type=str)
#end class

class WithdrawRequestSchema:
    parser = reqparse.RequestParser()
    parser.add_argument("amount", type=int)
    parser.add_argument("pin",    type=str)
#end class
