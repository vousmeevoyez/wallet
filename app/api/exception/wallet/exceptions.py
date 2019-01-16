class WalletError(Exception):
    """ Base Wallet Class Error"""
#end class

class WalletNotFoundError(WalletError):
    """ When wallet is not found """
    def __init__(self, source):
        super(WalletNotFoundError, self).__init__(source)
        self.msg = "Wallet {} is not found".format(source)

class WalletLockedError(WalletError):
    """ When source wallet is locked """

    def __init__(self, source):
        super(WalletLockedError, self).__init__(source)
        self.msg = "Wallet {} is locked".format(source)

class IncorrectPinError(WalletError):
    """ When incorrect pin entered"""
    def __init__(self):
        super(IncorrectPinError, self).__init__()
        self.msg = "Incorrect Pin"

class InsufficientBalanceError(WalletError):
    """ When balance is insufficient for transaction """
    def __init__(self, current_balance, amount):
        super(InsufficientBalanceError, self).__init__(current_balance, amount)
        self.msg = "Insufficient Balance"

class InvalidDestinationError(WalletError):
    """ When try to transfer destination and source is the same"""
    def __init__(self):
        super(InvalidDestinationError, self).__init__()
        self.msg = "Can't transfer to same wallet"

class TransactionError(WalletError):
    """ When something occured on database when creating transaction """
    def __init__(self, original_exception):
        super(TransactionError, self).__init__(original_exception)
        self.original_exception = original_exception

class TransferError(WalletError):
    """ raised when any kind of transfer failed"""
    def __init__(self, original_exception):
        super(TransferError, self).__init__(original_exception)
        self.msg = "Transfer Failed"
        self.original_exception = original_exception
