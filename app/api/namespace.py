from flask_restplus import Namespace

class UtilityNamespace:
    api = Namespace("utility")
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

class VirtualAccountNamespace:
    api = Namespace("virtual_account")
#end class

class CallbackNamespace:
    api = Namespace("callback")
#end class

class LogNamespace:
    api = Namespace("log")
#end class

class TransactionNamespace:
    api = Namespace("transactions")
#end class

class PaymentPlanNamespace:
    api = Namespace("payment_plans")
#end class
