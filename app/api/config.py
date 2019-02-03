"""
    Configuration
    _______________
    This is module for storing all configuration for various environments
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """ This is base class for configuration """
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_k3y')
    DEBUG = False
    BUNDLE_ERRORS = True #configuration key for flask-restplus to enable bundle erors

    DATABASE = {
        "DRIVER"   : os.getenv('DB_DRIVER') or "postgresql://", # sqlite // postgresql // mysql
        "USERNAME" : os.getenv('DB_USERNAME') or "modana",
        "PASSWORD" : os.getenv('DB_PASSWORD') or "passsword",
        "HOST_NAME": os.getenv('DB_HOSTNAME') or "localhost",
        "DB_NAME"  : os.getenv('DB_NAME') or "db_wallet",
    }

    CELERY_BROKER_URL = os.getenv("BROKER_URL") or 'amqp://guest:guest@localhost:5672'

    # JSON WEB TOKEN CONFIG
    JWT_CONFIG = {
        "SECRET"         : "wiqeuyashdkjlakssahn",
        "ALGORITHM"      : "HS256",
        "ACCESS_EXPIRE"  : 30, # minutes,
        "REFRESH_EXPIRE" : 30, # day,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # FLASK RESTPLUS
    ERROR_INCLUDE_MESSAGE = False

    STATUS_CONFIG = {
        "PENDING"  : 0,
        "ACTIVE"   : 1,
        "DEACTIVE" : 2,
        "LOCKED"   : 3,
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
        "DEPOSIT"            : 1,
        "IN_TRANSFER"        : 2,
        "OUT_TRANSFER"       : 3,
        "WITHDRAW"           : 4,
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

    ERROR_HEADER = {
        "USER_NOT_FOUND"    : "USER_ID_DOES_NOT_EXIST",
        "BANK_NOT_FOUND"    : "BANK_CODE_DOES_NOT_EXIST",
        "BANK_ACC_NOT_FOUND": "BANK_ACCOUNT_DOES_NOT_EXIST",
        "REVOKED_TOKEN"     : "REVOKED_TOKEN",
        "SIGNATURE_EXPIRED" : "SIGNATURE_EXPIRED",
        "INVALID_TOKEN"     : "INVALID_TOKEN",
        "DUPLICATE_BANK_ACC": "DUPLICATE_BANK_ACCOUNT",
        "DUPLICATE_USER"    : "DUPLICATE_USER",
        "DUPLICATE_WALLET"  : "DUPLICATE_WALLET",
        "ONLY_WALLET"       : "ONLY_WALLET",
        "INCORRECT_PIN"     : "INCORRECT_PIN",
        "PIN_NOT_MATCH"     : "PIN_NOT_MATCH",
        "PIN_NOT_MATCH"     : "PIN_NOT_MATCH",
        "DUPLICATE_PIN"     : "DUPLICATE_PIN",
        "PENDING_OTP"       : "PENDING_OTP",
    }

    # RESPONSE MESSAGE
    RESPONSE_MSG = {
        "SUCCESS" : {
            "CREATE_WALLET"         : "Wallet successfully created",
            "REMOVE_WALLET"         : "Wallet successfully removed",
            "LOCK_WALLET"           : "Wallet successfully locked",
            "UNLOCK_WALLET"         : "Wallet successfuly unlocked",
            "DEPOSIT"               : "Successfully Deposit {} to {}",
            "WITHDRAW"              : "Successfully Withdraw {} to {}",
            "TRANSFER"              : "Successfully Transfer {} from {} to {}",
            "REQUEST_WITHDRAW"      : "Request Withdraw Success",
            "CREATE_USER"           : "User & Wallet Successfully Created",
            "CREATE_BANK_ACCOUNT"   : "Bank Account Sucessfully Added",
            "UPDATE_BANK_ACCOUNT"   : "Bank Account Sucessfully Updated",
            "REMOVE_BANK_ACCOUNT"   : "Bank Account Succesfully Removed",
            "REMOVE_USER"           : "User successfully removed",
            "UPDATE_USER"           : "User information successfully updated",
            "ACCESS_AUTH"           : "Authentication success, Token generated",
            "REFRESH_AUTH"          : "Token Successfully refreshed",
            "LOGOUT_AUTH"           : "Access Token Successfully revoked",
            "LOGOUT_REFRESH"        : "Refresh Token Successfully revoked",
            "UPDATE_PIN"            : "Pin Successfully updated",
            "FORGOT_OTP"            : "Forgot OTP Code has been sent to {}",
            "FORGOT_PIN"            : "Forgot Pin Success",
        },
        "FAILED" : {
            "ERROR_ADDING_RECORD"    : "Duplicate Record",
            "INCORRECT_LOGIN"        : "Incorrect Login",
            "INCORRECT_PIN"          : "Incorrect Pin",
            "LOCK_WALLET"            : "Wallet already locked",
            "UNLOCK_WALLET"          : "Wallet already unlocked",
            "LOCK_TRANSACTION"       : "Cannot proceed transaction, Wallet is locked",
            "INSUFFICIENT_BALANCE"   : "Insufficient balance for this transaction",
            "ROLLBACK"               : "Transaction failed",
            "WITHDRAW_PENDING"       : "There's pending Withdraw Process\
                                        ,please wait {} before request again".
                                       format(VIRTUAL_ACCOUNT_CONFIG["BNI"]["DEBIT_VA_TIMEOUT"]),
            "WITHDRAW"               : "Request Withdraw Failed",
            "VA_CREATION"            : "Virtual Account Creation Failed",
            "WALLET_REMOVAL"         : "Can't remove the main wallet",
            "UNAUTHORIZED_WALLET"    : "Unauthorized Permission to Wallet",
            "UNAUTHORIZED_USER"      : "Unauthorized Permission to Access this user information",
            "MIN_WITHDRAW"           : "Minimum withdraw amount is {} ",
            "MAX_WITHDRAW"           : "Maximum withdraw amount is {} ",
            "UNKNOWN_ERROR"          : "Something wrong happen, Please"\
                                        "customer support if error persist",
            "VA_UPDATE_FAILED"       : "Failed updating Virtual Account",
            "EXPIRED_TOKEN"          : "Token has expired",
            "REVOKED_TOKEN"          : "Token has been revoked",
            "INVALID_TOKEN"          : "Invalid Token",
            "INSUFFICIENT_PERMISSION": "Admin Permission Required",
            "PIN_NOT_MATCH"          : "Pin & Confirm Pin does not match",
            "INVALID_OLD_PIN"        : "Wrong old pin",
            "OLD_PIN"                : "New Pin can't be the same with old one",
            "OTP_PENDING"            : "There's pending Forgot OTP, "\
                                       "Please wait {} minutes before request again".
                                       format(str(WALLET_CONFIG["OTP_TIMEOUT"])),
            "OTP_NOT_FOUND"          : "Invalid Forgot OTP Record",
            "INVALID_OTP_CODE"       : "Invalid OTP Code",
            "OTP_ALREADY_VERIFIED"   : "OTP Already verified",
            "REFRESH_TOKEN_ONLY"     : "Refresh Token Only",
            "INJECT"                 : "Fail injecting balance",
            "DEDUCT"                 : "Fail deducting balance",
            "BANK_ACCOUNT_NOT_FOUND" : "Bank Account not Found",
            "TRANSFER_FAILED"        : "Transfer Failed",
            "SMS_ERROR"              : "Sending SMS Failed",
        }
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
#end class


class DevelopmentConfig(Config):
    """ This is class for development configuration """
    DEBUG = True

    DATABASE = Config.DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
            DATABASE["DRIVER"] + DATABASE["USERNAME"] + ":" + \
            DATABASE["PASSWORD"] + "@" + DATABASE["HOST_NAME"] + "/" + \
            DATABASE["DB_NAME"] + "_dev"

    CELERY_RESULT_BACKEND = "db+" + DATABASE["DRIVER"] + DATABASE["USERNAME"]+\
                            ":" + DATABASE["PASSWORD"] + "@" +\
                            DATABASE["HOST_NAME"] +"/"+ DATABASE["DB_NAME"] +\
                            "_dev"

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
    PRESERVE_CONTEXT_ON_EXCEPTION = False
#end class


CONFIG_BY_NAME = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

KEY = Config.SECRET_KEY
