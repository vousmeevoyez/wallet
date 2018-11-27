import os

class Config(object):
    SECRET_KEY     = os.environ.get('SECRET_KEY') or "S3cret"
    # JSON WEB TOKEN CONFIG
    JWT_SECRET_KEY             = "MyS3cret"
    JWT_BLACKLIST_ENABLED      = True
    JWT_BLACKLIST_TOKEN_CHEKCS = [ "access", "refresh" ]
    # SQL ALCHEMY CONFIG
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'postgresql://modana:password@localhost/db_wallet'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # MASTER WALLET SETTINGS
    WALLET_CONFIG= {
        "MASTER_WALLET_ID"   : 1176785615,
        "PIN"                : 123456,
        "CREDIT_FLAG"        : True,
        "DEBIT_FLAG"         : False,
        "VA_TO_VA"           : 1,
        "BANK_TO_VA"         : 2,
        "VA_TO_BANK"         : 3,
        "CREDIT_VA_TIMEOUT"  : 4350, # 
        "CARDLESS_VA_TIMEOUT": 10, # 
        "MINIMAL_WITHDRAW"   : 50000, # 
        "MAX_WITHDRAW"       : 100000000, # 
        "MINIMAL_DEPOSIT"    : 50000, # 
        "MAX_DEPOSIT"        : 100000000, # 
        "VA_TIMEOUT"         : 87600, # set va expire to 10 years ago 
    }

    BANK_LIST_CONFIG = {
        "BNI" : 1,
    }

    USER_LEVEL_CONFIG = {
        "ADMIN" : 1,
        "USER"  : 2
    }

    VA_TYPE_CONFIG = {
        "CREDIT"   : 1,
        "CARDLESS" : 2
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
        "WALLET_NOT_FOUND"       : "{} Wallet not found",
        "ERROR_ADDING_RECORD"    : "Duplicate Record",
        "WALLET_CREATED"         : "Wallet successfully created",
        "WALLET_REMOVED"         : "Wallet successfully removed",
        "INCORRECT_LOGIN"        : "Incorrect Login",
        "INCORRECT_PIN"          : "Incorrect Pin",
        "WALLET_ALREADY_LOCKED"  : "Wallet already locked",
        "WALLET_LOCKED"          : "Wallet successfully locked",
        "WALLET_ALREADY_UNLOCKED": "Wallet already unlocked",
        "WALLET_UNLOCKED"        : "Wallet successfuly unlocked",
        "TRANSACTION_LOCKED"     : "Cannot proceed transaction, Wallet is locked",
        "INSUFFICIENT_BALANCE"   : "Insufficient balance for this transaction",
        "SUCCESS_DEPOSIT"        : "Successfully Deposit {} to {}",
        "SUCCESS_TRANSFER"       : "Successfully Transfer {} from {} to {}",
        "SUCCESS_WITHDRAW"       : "Successfully Withdraw {} from {}",
        "ROLLBACK_ERROR"         : "Transaction failed",
        "ALREADY_REQUESTED_ERROR": "Request already success, please wait before request again",
        "WITHDRAW_ERROR"         : "Request Withdraw Failed",
        "SUCCESS_WITHDRAW"       : "Request Withdraw Success",
        "TOPUP_ERROR"            : "Request Top Up Failed",
        "SUCCESS_TOPUP"          : "Request Top Up Success",
        "VA_CREATION_FAILED"     : "Virtual Account Creation Failed",
        "SUCCESS_CREATE_USER"    : "User & Wallet Successfully Created",
        "USER_REMOVED"           : "User successfully removed",
        "USER_UPDATED"           : "User information successfully updated",
        "WALLET_REMOVAL_FAILED"  : "Can't remove the main wallet",
        "SUCCESS_AUTH"           : "Authentication success, Token generated",
        "REFRESH_AUTH"           : "Token Successfully refreshed",
        "LOGOUT_AUTH"            : "Access Token Successfully revoked",
        "LOGOUT_REFRESH"         : "Refresh Token Successfully revoked",
        "UNAUTHORIZED_WALLET"    : "Unauthorized Permission to Wallet",
        "UNAUTHORIZED_USER"      : "Unauthorized Permission to Access this user information",
        "MIN_WITHDRAW_FAILED"    : "Minimum withdraw amount is {} ",
        "MAX_WITHDRAW_FAILED"    : "Maximum withdraw amount is {} ",
        "UNKNOWN_ERROR"          : "Something wrong happen, Please contact our customer support if error persist",
        "VA_UPDATE_FAILED"       : "Failed updating Virtual Account",
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
