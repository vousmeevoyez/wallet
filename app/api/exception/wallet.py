class WalletError(Exception):
    """ Base Wallet Class Error"""
#end class

class WalletNotFoundError(WalletError):
    """ When wallet is not found """
    msg = "Wallet not found"
    title = "WALLET_NOT_FOUND"

class WalletLockedError(WalletError):
    """ When source wallet is locked """

    def __init__(self, source):
        super(WalletLockedError, self).__init__(source)
        self.msg = "Wallet {} is locked".format(source)

class IncorrectPinError(WalletError):
    """ When incorrect pin entered"""
    msg = "Invalid Pin"
    title = "INCORRECT_PIN"

class UnmatchPinError(WalletError):
    """ When new and confirmed pin not same"""
    msg = "Pin and confirm pin not match"
    title = "PIN_NOT_MATCH"

class DuplicatePinError(WalletError):
    """ when new pin and old pin same"""
    msg = "New pin can't be same with the old one"
    title = "DUPLICATE_PIN"

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

class DuplicateWalletError(WalletError):
    """ raised when try create wallet that already existed """

class OnlyWalletError(WalletError):
    """ raised when try remove the only wallet left"""
    msg = "Can't remove main wallet"
    title = "ERROR_REMOVING_WALLET"

class PendingOtpError(WalletError):
    """ raised when try send otp but there are still pending request """
    msg = "there are pendng OTP request, please wait"
    title = "PENDING_OTP"

class WalletOtpError(WalletError):
    """ raised when try to send OTP but something wrong """
    msg = "Failed to Send OTP"
    title = "SEND_OTP_FAILED"

class OtpNotFoundError(WalletError):
    """ raised when try to verify OTP but record not found"""
    msg = "OTP request not found"
    title = "OTP_NOT_FOUND"

class OtpVerifiedError(WalletError):
    """ raised when try to verify OTP but already verified"""
    msg = "Otp already verified"
    title = "ALREADY_VERIFIED_OTP"

class InvalidOtpError(WalletError):
    """ raised when try to verify OTP but using invalid otp code"""
    msg = "Invalid Otp Code"
    title = "INVALID_OTP_CODE"

class TransactionDetailsNotFoundError(WalletError):
    """ raised when try view  transaaction details but details not found"""
    msg = "Transaction details not found"
    title = "TRX_DETAILS_NOT_FOUND"
