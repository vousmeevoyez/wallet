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
    "009": {
        "CREDIT_VA_TIMEOUT": 87600,  # 10 year
        "DEBIT_VA_TIMEOUT": 5,  # 10 minutes cardless
        "DEBIT_MAX_BALANCE": 2500000,  # allowed debit balance
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
    "TRANSFER_FEE": {"USER": 0, "CLEARING": 3500, "RTGS": 30000, "ONLINE": 6500},
    "OTP_TIMEOUT": 2,  # set otp timeout in minutes
    "INCORRECT_TIMEOUT": os.getenv("INCORRECT_TIMEOUT") or 5,
    "INCORRECT_RETRY": os.getenv("INCORRECT_RETRY") or 3,  # set max pin retry
    "QR_SECRET_KEY": "1#$@!%2jajdasnknvxivodisufu039021ofjldsjfa@@!",
    "LOCK_TIMEOUT": os.getenv("LOCK_TIMEOUT") or 5,
    "ALLOWED_BANK_CODES": ["009", "427"],  # BNI & BNI Syariah
}

LOGGING = {
    "TIMEOUT": os.getenv("NETWORK_TIMEOUT") or 15,
    "BNI_ECOLLECTION": "BNI-ECOLLECTION",
    "BNI_OPG": "BNI-OPG",
    "WAVECELL": "WAVECELL",
    "OUTGOING": 0,
    "INGOING": 1,
    "PAGE_SIZE": 100,
}

REPORTS = {"RECIPIENTS": os.getenv("REPORT_RECIPIENTS") or ["kelvin@modana.id"]}

ERROR = {
    "USER_NOT_FOUND": {"TITLE": "USER_NOT_FOUND", "MESSAGE": "User not found"},
    "BANK_NOT_FOUND": {"TITLE": "BANK_NOT_FOUND", "MESSAGE": "Bank not found"},
    "BANK_ACC_NOT_FOUND": {
        "TITLE": "BANK_ACC_NOT_FOUND",
        "MESSAGE": "Bank account not found",
    },
    "WALLET_NOT_FOUND": {"TITLE": "WALLET_NOT_FOUND", "MESSAGE": "Wallet not found"},
    "VA_NOT_FOUND": {"TITLE": "VA_NOT_FOUND", "MESSAGE": "Virtual Account not found"},
    "TRANSACTION_NOT_FOUND": {
        "TITLE": "TRANSACTION_NOT_FOUND",
        "MESSAGE": "Transaction not found",
    },
    "FORGOT_OTP_NOT_FOUND": {
        "TITLE": "FORGOT_OTP_NOT_FOUND",
        "MESSAGE": "Forgot OTP not found",
    },
    "PAYMENT_PLAN_NOT_FOUND": {
        "TITLE": "PAYMENT_PLAN_NOT_FOUND",
        "MESSAGE": "Payment Plan not Found",
    },
    "PLAN_NOT_FOUND": {"TITLE": "PLAN_NOT_FOUND", "MESSAGE": "Plan not Found"},
    "QUOTA_NOT_FOUND": {"TITLE": "QUOTA_NOT_FOUND", "MESSAGE": "Quota not Found"},
    "INVALID_CREDENTIALS": {
        "TITLE": "INVALID_CREDENTIALS",
        "MESSAGE": "Incorrect Username / Password",
    },
    "INVALID_DESTINATION": {
        "TITLE": "INVALID_DESTINATION",
        "MESSAGE": "Can't transfer to same wallet",
    },
    "INCORRECT_PIN": {"TITLE": "INCORRECT_PIN", "MESSAGE": "Incorrect Pin"},
    "MAX_PIN_ATTEMPT": {
        "TITLE": "MAX_PIN_ATTEMPT",
        "MESSAGE": "Entered an incorrect PIN too many times",
    },
    "WALLET_LOCKED": {
        "TITLE": "WALLET_LOCKED",
        "MESSAGE": "Too many attempts, please try again in 5 minutes. Your Modanaku is temporary locked",
    },
    "UNMATCH_PIN": {"TITLE": "UNMATCH_PIN", "MESSAGE": "Unmatch Pin and Confirm Pin"},
    "DUPLICATE_PIN": {
        "TITLE": "DUPLICATE_PIN",
        "MESSAGE": "New Pin Can't be the same with the old one",
    },
    "REVOKED_TOKEN": {"TITLE": "REVOKED_TOKEN", "MESSAGE": "Token has been revoked"},
    "SIGNATURE_EXPIRED": {
        "TITLE": "SIGNATURE_EXPIRED",
        "MESSAGE": "Token Signature Expired",
    },
    "INVALID_TOKEN": {"TITLE": "INVALID_TOKEN", "MESSAGE": "Invalid Token"},
    "EMPTY_PAYLOAD": {"TITLE": "EMPTY_PAYLOAD", "MESSAGE": "Empty Token Payload"},
    "INVALID_PARAMETER": {"TITLE": "INVALID_PARAMETER", "MESSAGE": "Invalid Parameter"},
    "BAD_AUTH_HEADER": {"TITLE": "INVALID_AUTHORIZATION_HEADER"},
    "ADMIN_REQUIRED": {
        "TITLE": "ADMIN_REQUIRED",
        "MESSAGE": "Require admin permission",
    },
    "ONLY_WALLET": {"TITLE": "ONLY_WALLET", "MESSAGE": "Can't remove main wallet"},
    "PENDING_OTP": {
        "TITLE": "PENDING_OTP",
        "MESSAGE": "there are pendng OTP request, please wait",
    },
    "PENDING_WITHDRAW": {
        "TITLE": "PENDING_WITHDRAW",
        "MESSAGE": "there are pendng Withdraw request, please wait",
    },
    "OTP_ALREADY_VERIFIED": {
        "TITLE": "OTP_ALREADY_VERIFIED",
        "MESSAGE": "OTP Already Verified",
    },
    "INVALID_OTP_CODE": {"TITLE": "INVALID_OTP_CODE", "MESSAGE": "Invalid OTP Code"},
    "INSUFFICIENT_BALANCE": {
        "TITLE": "INSUFFICIENT_BALANCE",
        "MESSAGE": "Insufficient Balance for this transaction",
    },
    "SMS_FAILED": {"TITLE": "SMS_FAILED", "MESSAGE": "Sending SMS OTP Failed"},
    "DUPLICATE_UPDATE_ENTRY": {
        "TITLE": "DUPLICATE_UPDATE_ENTRY",
        "MESSAGE": "Updated fields must be unique and can't be same with the old one",
    },
    "DUPLICATE_USER": {"TITLE": "DUPLICATE_USER", "MESSAGE": "User already existed"},
    "DUPLICATE_BANK_ACCOUNT": {
        "TITLE": "DUPLICATE_BANK_ACCOUNT",
        "MESSAGE": "Bank account already existed",
    },
    "DUPLICATE_WALLET": {
        "TITLE": "DUPLICATE_WALLET",
        "MESSAGE": "Wallet already existed",
    },
    "DUPLICATE_VA": {
        "TITLE": "DUPLICATE_VA",
        "MESSAGE": "Virtual Account already existed",
    },
    "DUPLICATE_PRODUCT": {
        "TITLE": "DUPLICATE_PRODUCT",
        "MESSAGE": "Product already existed",
    },
    "DUPLICATE_PAYMENT": {
        "TITLE": "DUPLICATE_PAYMENT",
        "MESSAGE": "Similiar payment already exist",
    },
    "DUPLICATE_PLAN_DUE_DATE": {
        "TITLE": "DUPLICATE_PLAN_DUE_DATE",
        "MESSAGE": "Similiar plan for that due date already exist",
    },
    "TRANSFER_FAILED": {"TITLE": "TRANSFER_FAILED", "MESSAGE": "Transfer failed"},
    "INVALID_REFUND": {"TITLE": "INVALID_REFUND", "MESSAGE": "Invalid Refund"},
    "TRANSACTION_REFUNDED": {
        "TITLE": "TRANSACTION_REFUNDED",
        "MESSAGE": "Transaction already refunded",
    },
    "MIN_WITHDRAW": {
        "TITLE": "MIN_WITHDRAW",
        "MESSAGE": "Amount can't be less than Minimal Withdraw",
    },
    "MAX_WITHDRAW": {
        "TITLE": "MAX_WITHDRAW",
        "MESSAGE": "Amount can't be more than Maximal Withdraw",
    },
    "DEPOSIT_CALLBACK_FAILED": {
        "TITLE": "DEPOSIT_CALLBACK_FAILED",
        "MESSAGE": "Deposit Callback failed, please contact our support",
    },
    "WITHDRAW_CALLBACK_FAILED": {
        "TITLE": "WITHDRAW_CALLBACK_FAILED",
        "MESSAGE": "Withdraw Callback failed, please contact our support",
    },
    "INVALID_ID": {"TITLE": "INVALID_ID", "MESSAGE": "Invalid Identifier"},
    "INVALID_CALLBACK": {"TITLE": "INVALID_CALLBACK", "MESSAGE": "Invalid Callback"},
    "INVALID_QR": {"TITLE": "INVALID_QR", "MESSAGE": "Invalid QR Code"},
    "BANK_PROCESS_FAILED": {
        "TITLE": "BANK_PROCESS_FAILED",
        "MESSAGE": "Bank failed to process the request",
    },
}
