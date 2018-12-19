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
        "ACCESS_EXPIRE"  : 30, # minutes,
        "REFRESH_EXPIRE" : 30, # day,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION  = False

    # FLASK RESTPLUS
    ERROR_INCLUDE_MESSAGE = False

    # MASTER WALLET SETTINGS
    WALLET_CONFIG= {
        "CREDIT_FLAG"        : True,
        "DEBIT_FLAG"         : False,
        "DEPOSIT"            : 1,
        "IN_TRANSFER"        : 2,
        "OUT_TRANSFER"       : 3,
        "WITHDRAW"           : 4,
        "CREDIT_VA_TIMEOUT"  : 4350, # 1 years 
        "CARDLESS_VA_TIMEOUT": 10, # 10 minutes
        "MINIMAL_WITHDRAW"   : 50000, # 
        "MAX_WITHDRAW"       : 100000000, # 
        "MINIMAL_DEPOSIT"    : 50000, # 
        "MAX_DEPOSIT"        : 100000000, # 
        "VA_TIMEOUT"         : 87600, # set va expire to 10 years ago 
        "OTP_TIMEOUT"        : 2 # set otp timeout in minutes
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
            "RECORD_NOT_FOUND"       : "Record not found",
            "ERROR_ADDING_RECORD"    : "Duplicate Record",
            "INCORRECT_LOGIN"        : "Incorrect Login",
            "INCORRECT_PIN"          : "Incorrect Pin",
            "LOCK_WALLET"            : "Wallet already locked",
            "UNLOCK_WALLET"          : "Wallet already unlocked",
            "LOCK_TRANSACTION"       : "Cannot proceed transaction, Wallet is locked",
            "INSUFFICIENT_BALANCE"   : "Insufficient balance for this transaction",
            "ROLLBACK"               : "Transaction failed",
            "WITHDRAW_PENDING"       : "There's pending Withdraw Process, please wait {} before request again".format(WALLET_CONFIG["CARDLESS_VA_TIMEOUT"]),
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
            "OTP_PENDING"            : "There's pending Forgot OTP, Please wait {} minutes before request again".format(str(WALLET_CONFIG["OTP_TIMEOUT"])),
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
        "CLIENT_NAME"   : "IDBNITU9EQU5B",
        "USERNAME"      : "041c7414-00fe-4338-98aa-b905ab5c2972",
        "PASSWORD"      : "894fe209-4c78-4c22-9925-a23ba36483f0",
        "API_KEY"       : "09ea583b-6d13-47ed-b675-9648f27826f2",
        "SECRET_API_KEY": "b854407e-33c9-4987-811d-72f7128b69f9",
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
        "TIMEOUT" : 3,
        "BNI_ECOLLECTION" : "BNI-ECOLLECTION",
        "BNI_OPG"         : "BNI-OPG",
        "OUTGOING"        : 0,
        "INGOING"         : 1,
    }

    SMS_SERVICES_CONFIG = {
        "BASE_URL"   : "https://api.wavecell.com/sms/v1/Modana_OTP/single",
        "API_KEY"    : "7hH72ACD8DA6EED4DD985D4489A034",
        "FROM"       : "MODANA",
    }

    SMS_OTP_ERRORS = {
        "FAILURE"    : "SMS OTP Failed",
        "TIMEOUT"    : "SMS OTP Services Timeout",
        "REDIRECT"   : "Bad URL",
        "EXCEPTION"  : "Something Unexpected Happen",
    }

    SMS_SERVICES_TEMPLATES = {
        "FORGOT_PIN" : "This is your FORGOT PIN Code for your Modanaku : {} . DON'T SHARE IT WITH ANYONE (NOT EVENT MODANA)",
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
