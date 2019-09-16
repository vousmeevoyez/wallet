"""
    All choices variable that is adjustable on wallet services
    ___________________________________
"""
import os

BACKGROUND_PAYMENT = {
    "DAY": os.getenv("PAYMENT_IN_DAY") or 60,  # minutes
    "COUNTDOWN": os.getenv("PAYMENT_COUNTDOWN") or 1,  # minutes
    "EXPIRES": os.getenv("PAYMENT_EXPIRES") or 1728000,  # SECONDS
}

WORKER = {
    "MAX_RETRIES": os.getenv("WORKER_MAX_RETRY") or 5,
    "HARD_LIMIT": 15,
    "SOFT_LIMIT": 10,
    "ACKS_LATE": True,  # prevent executing task twice
}

# JSON WEB TOKEN CONFIG
JWT = {
    "SECRET": os.getenv("JWT_SECRET") or "wiqeuyashdkjlakssahn",
    "ALGORITHM": "HS256",
    "ACCESS_EXPIRE": 30,  # minutes,
    "REFRESH_EXPIRE": 30,  # day,
}

STATUS = {"ACTIVE": 1, "DEACTIVE": 2, "LOCKED": 3}

TRANSACTION_LOG = {"DONE": 1, "CANCELLED": 2}

PAYMENT_STATUS = {"DONE": 1, "CANCELLED": 2}

VIRTUAL_ACCOUNT = {
    "BNI": {
        "CREDIT_VA_TIMEOUT": 4350,  # 1 year
        "DEBIT_VA_TIMEOUT": 5,  # 10 minutes cardless
    }
}

# MASTER WALLET SETTINGS
WALLET = {
    "CREDIT_FLAG": True,
    "DEBIT_FLAG": False,
    "MINIMAL_WITHDRAW": os.getenv("MINIMAL_WITHDRAW") or 50000,
    "MAX_WITHDRAW": os.getenv("MAX_WITHDRAW") or 100000000,
    "MINIMAL_DEPOSIT": os.getenv("MINIMAL_DEPOSIT") or 50000,
    "MAX_DEPOSIT": os.getenv("MAX_DEPOSIT") or 100000000,
    "TRANSFER_FEE": {"USER": 0, "CLEARING": 5000, "RTGS": 30000, "ONLINE": 6500},
    "OTP_TIMEOUT": 2,  # set otp timeout in minutes
    "INCORRECT_TIMEOUT": os.getenv("INCORRECT_TIMEOUT") or 5,
    "INCORRECT_RETRY": os.getenv("INCORRECT_RETRY") or 3,  # set max pin retry
    "QR_SECRET_KEY": "1#$@!%2jajdasnknvxivodisufu039021ofjldsjfa@@!",
    "LOCK_TIMEOUT": os.getenv("LOCK_TIMEOUT") or 5,
}

LOGGING = {
    "TIMEOUT": 5,
    "BNI_ECOLLECTION": "BNI-ECOLLECTION",
    "BNI_OPG": "BNI-OPG",
    "WAVECELL": "WAVECELL",
    "OUTGOING": 0,
    "INGOING": 1,
    "PAGE_SIZE": 100,
}
