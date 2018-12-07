import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_k3y')
    DEBUG = False
    BUNDLE_ERRORS = True #configuration key for flask-restplus to enable bundle erors

    # JSON WEB TOKEN CONFIG
    JWT_CONFIG = {
        "SECRET"         : "wiqeuyashdkjlakssahn",
        "ACCESS_EXPIRE"  : 10, # minutes,
        "REFRESH_EXPIRE" : 30, # day,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION  = False

    # MASTER WALLET SETTINGS
    WALLET_CONFIG= {
        "CREDIT_FLAG"        : True,
        "DEBIT_FLAG"         : False,
        "VA_TO_VA"           : 1,
        "BANK_TO_VA"         : 2,
        "VA_TO_BANK"         : 3,
        "CREDIT_VA_TIMEOUT"  : 4350, # 1 years 
        "CARDLESS_VA_TIMEOUT": 10, # 10 minutes
        "MINIMAL_WITHDRAW"   : 50000, # 
        "MAX_WITHDRAW"       : 100000000, # 
        "MINIMAL_DEPOSIT"    : 50000, # 
        "MAX_DEPOSIT"        : 100000000, # 
        "VA_TIMEOUT"         : 87600, # set va expire to 10 years ago 
        "OTP_TIMEOUT"        : 5 # set otp timeout in minutes
    }

    # MASTER WALLET SETTINGS
    TRANSACTION_NOTES= {
        "DEPOSIT"         : "Top up balance {} from Virtual Account {}, Reference Number {}",
        "INJECT"          : "Injected balance {}",
        "SEND_TRANSFER"   : "Transfer balance {}",
        "RECEIVE_TRANSFER": "Received balance {}",
        "WITHDRAW_NOTIF"  : "Withdraw balance {} from Virtual Account {}, Reference Number {}"
    }

    # RESPONSE MESSAGE
    RESPONSE_MSG = {
        "SUCCESS" : {
            "CREATE_WALLET"         : "Wallet successfully created",
            "REMOVE_WALLET"         : "Wallet successfully removed",
            "LOCK_WALLET"           : "Wallet successfully locked",
            "UNLOCK_WALLET"         : "Wallet successfuly unlocked",
            "DEPOSIT"               : "Successfully Deposit {} to {}",
            "TRANSFER"              : "Successfully Transfer {} from {} to {}",
            "REQUEST_WITHDRAW"      : "Request Withdraw Success",
            "CREATE_USER"           : "User & Wallet Successfully Created",
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
            "RECORD_NOT_FOUND"       : "Record not found",
            "ERROR_ADDING_RECORD"    : "Duplicate Record",
            "INCORRECT_LOGIN"        : "Incorrect Login",
            "INCORRECT_PIN"          : "Incorrect Pin",
            "LOCK_WALLET"            : "Wallet already locked",
            "UNLOCK_WALLET"          : "Wallet already unlocked",
            "LOCK_TRANSACTION"       : "Cannot proceed transaction, Wallet is locked",
            "INSUFFICIENT_BALANCE"   : "Insufficient balance for this transaction",
            "ROLLBACK"               : "Transaction failed",
            "EXIST_WITHDRAW"         : "Request already success, please wait before request again",
            "WITHDRAW"               : "Request Withdraw Failed",
            "VA_CREATION"            : "Virtual Account Creation Failed",
            "WALLET_REMOVAL"         : "Can't remove the main wallet",
            "UNAUTHORIZED_WALLET"    : "Unauthorized Permission to Wallet",
            "UNAUTHORIZED_USER"      : "Unauthorized Permission to Access this user information",
            "MIN_WITHDRAW"           : "Minimum withdraw amount is {} ",
            "MAX_WITHDRAW"           : "Maximum withdraw amount is {} ",
            "UNKNOWN_ERROR"          : "Something wrong happen, Please contact our customer support if error persist",
            "VA_UPDATE_FAILED"       : "Failed updating Virtual Account",
            "EXPIRED_TOKEN"          : "Token has expired",
            "REVOKED_TOKEN"          : "Token has been revoked",
            "INVALID_TOKEN"          : "Invalid Token",
            "INSUFFICIENT_PERMISSION": "Admin Permission Required",
            "PIN_NOT_MATCH"          : "Pin & Confirm Pin does not match",
            "OLD_PIN"                : "New Pin can't be the same with old one",
            "OTP_PENDING"            : "There's pending Forgot OTP, Please wait 5 minutes before request again",
            "OTP_NOT_FOUND"          : "Invalid Forgot OTP Record",
            "INVALID_OTP_CODE"       : "Invalid OTP Code",
            "OTP_ALREADY_VERIFIED"   : "OTP Already verified",
            "REFRESH_TOKEN_ONLY"     : "Only Refresh Token Allowed",
            "INJECT"                 : "Fail injecting balance",
            "DEDUCT"                 : "Fail deducting balance",
        }
    }

    # BNI E-COLLECTION ERROR MSG
    BNI_ECOLLECTION_ERROR_HANDLER= {
        "VA_ERROR"      : "VA failed to create",
        "INQUIRY_ERROR" : "Get Inquiry failed",
        "UPDATE_ERROR " : "Update VA Transaction failed",
    }

    # BNI E-COLLECTION CONFIG
    BNI_ECOLLECTION_CONFIG = {
        "BASE_URL_DEV"     : "https://apibeta.bni-ecollection.com/",
        "BASE_URL_PROD"    : "https://apibeta.bni-ecollection.com/",
        "DEBIT_SECRET_KEY" : "8eafc8687722fdd0ef78942309fcd983",
        "CREDIT_SECRET_KEY": "707e501f79c05001a376636c10f7b8cf",
        "DEBIT_CLIENT_ID"  : "99099",
        "CREDIT_CLIENT_ID" : "99098",
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
        "BASE_URL_DEV"  : "https://apidev.bni.co.id",
        "PORT"          : "8066",
        "CLIENT_ID"     : "IDBNIQk5JU0VSVklDRQ==",
        "USERNAME"      : "ab4e9e87-3b2c-4ed0-87bf-f807ae9b17e1",
        "PASSWORD"      : "ff915349-cbc6-4b9e-acfd-c727df960ded",
        "ROUTES"        : {
            "GET_TOKEN"  : "/api/oauth/token",
            "GET_BALANCE": "/H2H/getbalance",
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
        "TIMEOUT" : 3,
        "BNI_ECOLLECTION" : "BNI-ECOLLECTION",
        "BNI_OPG"         : "BNI-OPG",
        "OUTGOING"        : 0,
        "INGOING"         : 1,
    }

    SMS_SERVICES_CONFIG = {
        "API_KEY"    : "1ae57f88",
        "SECRET_KEY" : "t1sXmOVCPCJapQ0m",
        "FROM"       : "Modanaku",
    }

    SMS_SERVICES_TEMPLATES = {
        "FORGOT_PIN" : "This is your FORGOT PASSWORD CODE for your Modanaku : {} . DON'T SHARE IT WITH ANYONE (NOT EVENT MODANA)",
    }
#end class


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'postgresql://modana:password@localhost/db_wallet'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
#end class


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
#end class


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'postgresql://postgres:secret@db/postgres'
#end class


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
