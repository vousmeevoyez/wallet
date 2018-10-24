import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "S3cret"
    # SQL ALCHEMY CONFIG
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MASTER WALLET SETTINGS
    WALLET_CONFIG= {
        "MASTER_WALLET_ID" : 114620581380,
        "CREDIT_FLAG"      : True,
        "DEBIT_FLAG"       : False,
        "VA_TO_VA"         : 1,
        "BANK_TO_VA"       : 2,
        "VA_TO_BANK"       : 3,
    }

    # MASTER WALLET SETTINGS
    TRANSACTION_NOTES= {
        "DEPOSIT" : "Top up balance {}",
        "INJECT"  : "Injected balance {}",
    }

    # RESPONSE MESSAGE
    RESPONSE_MSG = {
        "WALLET_NOT_FOUND"       : "{} Wallet not found",
        "ERROR_ADDING_RECORD"    : "Error adding record",
        "WALLET_CREATED"         : "Wallet successfully created",
        "INCORRECT_PIN"          : "Incorrect Pin",
        "WALLET_ALREADY_LOCKED"  : "Wallet already locked",
        "WALLET_LOCKED"          : "Wallet successfully locked",
        "WALLET_ALREADY_UNLOCKED": "Wallet already unlocked",
        "WALLET_UNLOCKED"        : "Wallet successfuly unlocked",
        "TRANSACTION_LOCKED"     : "Cannot proceed transaction, Wallet is locked",
        "INSUFFICIENT_BALANCE"   : "Insufficient balance for this transaction",
        "SUCCESS_DEPOSIT"        : "Successfully Deposit {} to {}",
        "SUCCESS_TRANSFER"       : "Successfully Transfer {} to {}",
        "ROLLBACK_ERROR"         : "Transaction failed",
    }

    # BNI E-COLLECTION CONFIG
    BNI_ECOLLECTION_CONFIG = {
        "BASE_URL_DEV"  : "https://apibeta.bni-ecollection.com/",
        "BASE_URL_PROD" : "https://apibeta.bni-ecollection.com/",
        "SECRET_KEY"    : "8eafc8687722fdd0ef78942309fcd983",
        "CLIENT_ID"     : "99099",
        "BILLING_TYPE"  : "J",
    }

    # BNI OPG CONFIG
    BNI_OPG_CONFIG = {
        "BASE_URL_DEV"  : "https://apibeta.bni-ecollection.com/",
        "BASE_URL_PROD" : "https://apibeta.bni-ecollection.com/",
        "SECRET_KEY"    : "8eafc8687722fdd0ef78942309fcd983",
        "CLIENT_ID"     : "99099",
        "BILLING_TYPE"  : "J",
    }

    # ACCESS_KEY CONFIG
    ACCESS_KEY_CONFIG = {
        "TOKEN_LENGTH" : 20,
        "EXPIRE_IN"    : 525600 # 1 year in minutes
    }
