"""
    All Exception Raised in COmmon BluePrint
"""


class CommonError(Exception):
    """ Exception raised on common blueprint """


class SmsError(CommonError):
    """ Exception raised when failed send an sms """


class DecryptError(CommonError):
    """ Exception raised when failed decrypting QR """
