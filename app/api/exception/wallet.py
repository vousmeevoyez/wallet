""" 
    WALLET EXCEPTION
"""
from app.config     import config

WALLET_CONFIG = config.Config.WALLET_CONFIG

class WalletError(Exception):
    """ Base Wallet Class Error"""
#end class

class WalletNotFoundError(WalletError):
    """ When wallet is not found """
    def __init__(self, origin):
        super().__init__(origin)
        self.msg = "{} Wallet not found".format(origin)
        self.title = "WALLET_NOT_FOUND"

class WalletLockedError(WalletError):
    """ When source wallet is locked """

    def __init__(self, source):
        super(WalletLockedError, self).__init__(source)
        self.msg = "Wallet {} is locked".format(source)
        self.title = "WALLET_LOCKED"

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
        self.msg = "Insufficient Balance, current balance {} but required\
        amount {}".format(current_balance, amount)
        self.title = "INSUFFICIENT_BALANCE"

class InvalidDestinationError(WalletError):
    """ When try to transfer destination and source is the same"""
    msg = "Can't transfer to same wallet"
    title = "INVALID_DESTINATION"

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
    msg = "Wallet Already Existed"
    title = "WALLET_ALREADY_EXISTED"

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

class TransactionNotFoundError(WalletError):
    """ raised when try view  transaaction but not found"""
    msg = "Transaction not found"
    title = "TRANSACTION_NOT_FOUND"

class MinimalWithdrawError(WalletError):
    """ raises when user try to withdraw less than minimal amount """
    msg = "Minimal withdraw amount is {}".format(WALLET_CONFIG["MINIMAL_WITHDRAW"])
    title = "MINIMAL_WITHDRAW"

class MaxWithdrawError(WalletError):
    """ raises when user try to withdraw more than maximal amount """
    msg = "Maximal withdraw amount is {}".format(WALLET_CONFIG["MAX_WITHDRAW"])
    title = "MAX_WITHDRAW"

class RaisePendingWithdrawError(WalletError):
    """ raises when user try to withdraw but already pending withraw request """
    msg = "There's pending withdraw occured"
    title = "PENDING_WITHDRAW_REQUEST"
