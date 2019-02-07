from flask_restplus import Namespace

class CommonNamespace:
    api = Namespace("common")
#end class

class AuthNamespace:
    api = Namespace("authentication")
#end class

class UserNamespace:
    api = Namespace("user")
#end class

class WalletNamespace:
    api = Namespace("wallet")
#end class

class BankNamespace:
    api = Namespace("bank")
#end class

class CallbackNamespace:
    api = Namespace("callback")
#end class

class LogNamespace:
    """ logging prupose """
    api = Namespace("log")
#end class

class ExceptionNamespace:
    """ for register exception errorhandler"""
    api = Namespace("exception")
#end class
