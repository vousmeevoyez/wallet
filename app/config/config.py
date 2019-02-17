"""
    Configuration
    _______________
    This is module for storing all configuration for various environments
"""
from kombu import Connection, Exchange, Queue

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """ This is base class for configuration """
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_k3y')
    DEBUG = False
    BUNDLE_ERRORS = True #configuration key for flask-restplus to enable bundle erors

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # FLASK RESTPLUS
    ERROR_INCLUDE_MESSAGE = False

    DATABASE = {
        "DRIVER"   : os.getenv('DB_DRIVER') or "postgresql://", # sqlite // postgresql // mysql
        "USERNAME" : os.getenv('DB_USERNAME') or "modana",
        "PASSWORD" : os.getenv('DB_PASSWORD') or "passsword",
        "HOST_NAME": os.getenv('DB_HOSTNAME') or "localhost",
        "DB_NAME"  : os.getenv('DB_NAME') or "db_wallet",
    }

    SENTRY_CONFIG = {}

    CELERY_BROKER_URL = os.getenv("BROKER_URL") or \
    'amqp://guest:guest@localhost:5672'
    #CELERY_QUEUES = (
    #    Queue('bank', Exchange('bank'), routing_key='bank')
    #)

    WORKER_CONFIG = {
        "MAX_RETRIES" : 5,
        "HARD_LIMIT"  : 15,
        "SOFT_LIMIT"  : 10,
        "ACKS_LATE"   : True # prevent executing task twice
    }

    # JSON WEB TOKEN CONFIG
    JWT_CONFIG = {
        "SECRET"         : "wiqeuyashdkjlakssahn",
        "ALGORITHM"      : "HS256",
        "ACCESS_EXPIRE"  : 30, # minutes,
        "REFRESH_EXPIRE" : 30, # day,
    }

    STATUS_CONFIG = {
        "PENDING"  : 0,
        "ACTIVE"   : 1,
        "DEACTIVE" : 2,
        "LOCKED"   : 3,
    }

    TRANSACTION_LOG_CONFIG = {
        "PENDING"  : 0,
        "DONE"     : 1,
        "CANCELLED": 2,
    }

    PAYMENT_STATUS_CONFIG = {
        "PENDING"  : 0,
        "DONE"     : 1,
        "CANCELLED": 2,
    }

    VIRTUAL_ACCOUNT_CONFIG = {
        "BNI" : {
            "CREDIT_VA_TIMEOUT"  : 4350, # 1 year
            "DEBIT_VA_TIMEOUT": 10, # 10 minutes cardless
        }
    }

    # MASTER WALLET SETTINGS
    WALLET_CONFIG = {
        "CREDIT_FLAG"        : True,
        "DEBIT_FLAG"         : False,
        "MINIMAL_WITHDRAW"   : 50000,
        "MAX_WITHDRAW"       : 100000000,
        "MINIMAL_DEPOSIT"    : 50000,
        "MAX_DEPOSIT"        : 100000000,
        "OTP_TIMEOUT"        : 2, # set otp timeout in minutes
        "QR_SECRET_KEY"      : "1#$@!%2jajdasnknvxivodisufu039021ofjldsjfa@@!"
    }

    TRANSACTION_CONFIG = {
        "TYPES" : {
            "TOP_UP"      : 1,
            "WITHDRAW"    : 2,
            "TRANSFER_IN" : 3, # transfer between user
            "TRANSFER_OUT": 4, # transfer to external system
            "RECEIVE_TRANSFER": 5
        }
    }

    # MASTER WALLET SETTINGS
    TRANSACTION_NOTES = {
        "DEPOSIT"         : "Top up balance {} from Virtual Account",
        "INJECT"          : "Injected balance {}",
        "SEND_TRANSFER"   : "Transfer balance {}",
        "RECEIVE_TRANSFER": "Received balance {}",
        "WITHDRAW_NOTIF"  : "Withdraw balance {} from Virtual Account"
    }

    # BNI E-COLLECTION CONFIG
    BNI_ECOLLECTION_CONFIG = {
        "BASE_URL"         : os.getenv('BNI_VA_URL') or \
        "https://apibeta.bni-ecollection.com/",
        "DEBIT_SECRET_KEY" : os.getenv('BNI_VA_DEBIT_SECRET_KEY') or \
        "8eafc8687722fdd0ef78942309fcd983",
        "CREDIT_SECRET_KEY": os.getenv('BNI_VA_CREDIT_SECRET_KEY') or \
        "707e501f79c05001a376636c10f7b8cf",
        "DEBIT_CLIENT_ID"  : os.getenv('BNI_VA_DEBIT_CLIENT_ID') or "99099",
        "CREDIT_CLIENT_ID" : os.getenv('BNI_VA_CREDIT_CLIENT_ID') or "99098",
        "BILLING"          : "createbilling",
        "CARDLESS"         : "createdebitcardless",
        "UPDATE"           : "updatebilling",
        "INQUIRY"          : "inquirybilling",
        #"CREDIT_BILLING_TYPE"   : "z",
        "CREDIT_BILLING_TYPE"   : "o", #open payment
        "CARDLESS_BILLING_TYPE" : "j",
    }

    # BNI OPG CONFIG
    BNI_OPG_CONFIG = {
        "MASTER_ACCOUNT": os.getenv('BNI_MASTER_ACCOUNT') or "0115476117",
        "BASE_URL_DEV"  : os.getenv('BNI_OPG_URL') or "https://apidev.bni.co.id",
        "PORT"          : os.getenv('BNI_OPG_PORT') or "8066",
        "CLIENT_NAME"   : os.getenv('BNI_OPG_CLIENT_NAME') or "IDBNITU9EQU5B",
        "USERNAME"      : os.getenv('BNI_OPG_USERNAME') or \
        "041c7414-00fe-4338-98aa-b905ab5c2972",
        "PASSWORD"      : os.getenv('BNI_OPG_PASSWORD') or \
        "894fe209-4c78-4c22-9925-a23ba36483f0",
        "API_KEY"       : os.getenv('BNI_OPG_API_KEY') or \
        "09ea583b-6d13-47ed-b675-9648f27826f2",
        "SECRET_API_KEY": os.getenv('BNI_OPG_SECRET_API_KEY') or \
        "b854407e-33c9-4987-811d-72f7128b69f9",
        "ROUTES"        : {
            "GET_TOKEN"            : "/api/oauth/token",
            "GET_BALANCE"          : "/H2H/v2/getbalance",
            "GET_INHOUSE_INQUIRY"  : "/H2H/v2/getinhouseinquiry",
            "DO_PAYMENT"           : "/H2H/v2/dopayment",
            "GET_PAYMENT_STATUS"   : "/H2H/v2/getpaymentstatus",
            "GET_INTERBANK_INQUIRY": "/H2H/v2/getinterbankinquiry",
            "GET_INTERBANK_PAYMENT": "/H2H/v2/getinterbankpayment",
            "HOLD_AMOUNT"          : "/H2H/v2/holdamount",
            "HOLD_AMOUNT_RELEASE"  : "/H2H/v2/holdamountrelease",
        }
    }

    # ACCESS_KEY CONFIG
    ACCESS_KEY_CONFIG = {
        "TOKEN_LENGTH" : 20,
        #"EXPIRE_IN"    : 525600 # 1 year in minutes
        "EXPIRE_IN"    : 8760 # 1 year in hour
    }

    # logging config
    LOGGING_CONFIG = {
        "TIMEOUT" : 10,
        "BNI_ECOLLECTION" : "BNI-ECOLLECTION",
        "BNI_OPG"         : "BNI-OPG",
        "WAVECELL"        : "WAVECELL",
        "OUTGOING"        : 0,
        "INGOING"         : 1,
    }

    SMS_SERVICES_CONFIG = {
        "BASE_URL"   : os.getenv('SMS_SERVICES_BASE_URL') or \
        "https://api.wavecell.com/sms/v1/Modana_OTP/single",
        "API_KEY"    : os.getenv('API_KEY') or \
        "7hH72ACD8DA6EED4DD985D4489A034",
        "FROM"       : "MODANA",
    }

    SMS_SERVICES_TEMPLATES = {
        "FORGOT_PIN" : "This is your FORGOT PIN Code for your Modanaku : {}."\
        "DON'T SHARE IT WITH ANYONE (NOT EVENT MODANA)",
    }

    ERROR_CONFIG = {
        "USER_NOT_FOUND" : {
            "TITLE"   : "USER_NOT_FOUND",
            "MESSAGE" : "User not found"
        },
        "BANK_NOT_FOUND" : {
            "TITLE"   : "BANK_NOT_FOUND",
            "MESSAGE" : "Bank not found"
        },
        "BANK_ACC_NOT_FOUND" : {
            "TITLE"   : "BANK_ACC_NOT_FOUND",
            "MESSAGE" : "Bank account not found"
        },
        "WALLET_NOT_FOUND" : {
            "TITLE"   : "WALLET_NOT_FOUND",
            "MESSAGE" : "Wallet not found"
        },
        "VA_NOT_FOUND" : {
            "TITLE"   : "VA_NOT_FOUND",
            "MESSAGE" : "Virtual Account not found"
        },
        "WALLET_LOCKED" : {
            "TITLE"   : "WALLET_LOCKED",
            "MESSAGE" : "Wallet is locked"
        },
        "TRANSACTION_NOT_FOUND" : {
            "TITLE"   : "TRANSACTION_NOT_FOUND",
            "MESSAGE" : "Transaction not found"
        },
        "FORGOT_OTP_NOT_FOUND" : {
            "TITLE"   : "FORGOT_OTP_NOT_FOUND",
            "MESSAGE" : "Forgot OTP not found"
        },
        "INVALID_CREDENTIALS" : {
            "TITLE"   : "INVALID_CREDENTIALS",
            "MESSAGE" : "Incorrect Username / Password"
        },
        "INVALID_DESTINATION" : {
            "TITLE"   : "INVALID_DESTINATION",
            "MESSAGE" : "Can't transfer to same wallet"
        },
        "INCORRECT_PIN" : {
            "TITLE"   : "INCORRECT_PIN",
            "MESSAGE" : "Incorrect Pin"
        },
        "UNMATCH_PIN" : {
            "TITLE"   : "UNMATCH_PIN",
            "MESSAGE" : "Unmatch Pin and Confirm Pin"
        },
        "DUPLICATE_PIN" : {
            "TITLE"   : "DUPLICATE_PIN",
            "MESSAGE" : "New Pin Can't be the same with the old one"
        },
        "REVOKED_TOKEN" : {
            "TITLE"   : "REVOKED_TOKEN",
            "MESSAGE" : "Token has been revoked"
        },
        "SIGNATURE_EXPIRED" : {
            "TITLE"   : "SIGNATURE_EXPIRED",
            "MESSAGE" : "Token Signature Expired"
        },
        "INVALID_TOKEN" : {
            "TITLE"   : "INVALID_TOKEN",
            "MESSAGE" : "Invalid Token"
        },
        "EMPTY_PAYLOAD" : {
            "TITLE"   : "EMPTY_PAYLOAD",
            "MESSAGE" : "Empty Token Payload"
        },
        "INVALID_PARAMETER" : {
            "TITLE"  : "INVALID_PARAMETER",
            "MESSAGE": "Invalid Parameter",
        },
        "BAD_AUTH_HEADER" : {
            "TITLE" : "INVALID_AUTHORIZATION_HEADER",
        },
        "ADMIN_REQUIRED" : {
            "TITLE"   : "ADMIN_REQUIRED",
            "MESSAGE" : "Require admin permission"
        },
        "ONLY_WALLET" : {
            "TITLE" : "ONLY_WALLET",
            "MESSAGE" : "Can't remove main wallet"
        },
        "PENDING_OTP" : {
            "TITLE"   : "PENDING_OTP",
            "MESSAGE" : "there are pendng OTP request, please wait"
        },
        "PENDING_WITHDRAW" : {
            "TITLE"   : "PENDING_WITHDRAW",
            "MESSAGE" : "there are pendng Withdraw request, please wait"
        },
        "OTP_ALREADY_VERIFIED" : {
            "TITLE"   : "OTP_ALREADY_VERIFIED",
            "MESSAGE" : "OTP Already Verified"
        },
        "INVALID_OTP_CODE" : {
            "TITLE"   : "INVALID_OTP_CODE",
            "MESSAGE" : "Invalid OTP Code"
        },
        "INSUFFICIENT_BALANCE" : {
            "TITLE"   : "INSUFFICIENT_BALANCE",
            "MESSAGE" : "Insufficient Balance for this transaction"
        },
        "SMS_FAILED" : {
            "TITLE"   : "SMS_FAILED",
            "MESSAGE" : "Sending SMS OTP Failed"
        },
        "DUPLICATE_UPDATE_ENTRY" : {
            "TITLE"  : "DUPLICATE_UPDATE_ENTRY",
            "MESSAGE": "Updated fields must be unique and can't be same with\
            the old one"
        },
        "DUPLICATE_USER" : {
            "TITLE"   : "DUPLICATE_USER",
            "MESSAGE" : "User already existed"
        },
        "DUPLICATE_BANK_ACCOUNT" : {
            "TITLE"   : "DUPLICATE_BANK_ACCOUNT",
            "MESSAGE" : "Bank account already existed"
        },
        "DUPLICATE_WALLET" : {
            "TITLE"   : "DUPLICATE_WALLET",
            "MESSAGE" : "Wallet already existed"
        },
        "DUPLICATE_VA" : {
            "TITLE"   : "DUPLICATE_VA",
            "MESSAGE" : "Virtual Account already existed"
        },
        "TRANSFER_FAILED" : {
            "TITLE"   : "TRANSFER_FAILED",
            "MESSAGE" : "Transfer failed"
        },
        "MIN_WITHDRAW": {
            "TITLE"   : "MIN_WITHDRAW",
            "MESSAGE" : "Amount can't be less than Minimal Withdraw"
        },
        "MAX_WITHDRAW": {
            "TITLE"   : "MAX_WITHDRAW",
            "MESSAGE" : "Amount can't be more than Maximal Withdraw"
        },
        "DEPOSIT_CALLBACK_FAILED": {
            "TITLE"   : "DEPOSIT_CALLBACK_FAILED",
            "MESSAGE" : "Deposit Callback failed, please contact our support"
        },
        "WITHDRAW_CALLBACK_FAILED": {
            "TITLE"   : "WITHDRAW_CALLBACK_FAILED",
            "MESSAGE" : "Withdraw Callback failed, please contact our support"
        },
        "INVALID_CALLBACK": {
            "TITLE"   : "INVALID_CALLBACK",
            "MESSAGE" : "Invalid Callback"
        },
        "INVALID_QR": {
            "TITLE"   : "INVALID_QR",
            "MESSAGE" : "Invalid QR Code"
        },
    }
#end class


class DevelopmentConfig(Config):
    """ This is class for development configuration """
    DEBUG = True

    DATABASE = Config.DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
            DATABASE["DRIVER"] + DATABASE["USERNAME"] + ":" + \
            DATABASE["PASSWORD"] + "@" + DATABASE["HOST_NAME"] + "/" + \
            DATABASE["DB_NAME"] + "_dev"

    CELERY_RESULT_BACKEND = "db+" + SQLALCHEMY_DATABASE_URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False
#end class


class TestingConfig(Config):
    """ This is class for testing configuration """
    DEBUG = True
    TESTING = True

    DATABASE = Config.DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
            DATABASE["DRIVER"] + DATABASE["USERNAME"] + ":" + \
            DATABASE["PASSWORD"] + "@" + DATABASE["HOST_NAME"] + "/" + \
            DATABASE["DB_NAME"] + "_testing"

    CELERY_RESULT_BACKEND = "db+" + SQLALCHEMY_DATABASE_URI

    CELERY_TASK_ALWAYS_EAGER = True

    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
#end class


class ProductionConfig(Config):
    """ This is class for production configuration """
    DEBUG = False

    DATABASE = Config.DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
            DATABASE["DRIVER"] + DATABASE["USERNAME"] + ":" + \
            DATABASE["PASSWORD"] + "@" + DATABASE["HOST_NAME"] + "/" + \
            DATABASE["DB_NAME"] + "_prod"

    CELERY_RESULT_BACKEND = "db+" + SQLALCHEMY_DATABASE_URI

    PRESERVE_CONTEXT_ON_EXCEPTION = False

    SENTRY_CONFIG = Config.SENTRY_CONFIG
    SENTRY_CONFIG["dsn"] = "https://c864361a612b47a3827e2c5b3280a727:24dd1b18103842159d31e273a369ce56@sentry.io/1385947"
#end class


CONFIG_BY_NAME = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

KEY = Config.SECRET_KEY
