"""
    Bank Exception
"""

class BaseError(Exception):
    """ base error class"""

class BankNotFoundError(BaseError):
    """" raised when bank id not found """
    msg = "Bank Not Found"
    title = "BANK_ID_DOES_NOT_EXIST"

class DuplicateBankAccountError(BaseError):
    """" raised when try create same bank account"""
    msg = "Bank Account already exist"
    title = "DUPLICATE_BANK_ACCOUNT"

class BankAccountNotFoundError(BaseError):
    """" raised when bank account not found """
    msg = "Bank Account Not Found"
    title = "BANK_ACC_ID_DOES_NOT_EXIST"
