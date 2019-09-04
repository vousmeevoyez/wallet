import os

BNI_ECOLLECTION = {
    "BASE_URL"         : os.getenv('BNI_VA_URL') or \
    "https://apibeta.bni-ecollection.com/",
    "DEBIT_SECRET_KEY" : os.getenv('BNI_VA_DEBIT_SECRET_KEY') or \
    "8eafc8687722fdd0ef78942309fcd983",
    "DEBIT_CLIENT_ID"  : os.getenv('BNI_VA_DEBIT_CLIENT_ID') or "99099",
    "CREDIT_SECRET_KEY": os.getenv('BNI_VA_CREDIT_SECRET_KEY') or \
    "707e501f79c05001a376636c10f7b8cf",
    "CREDIT_CLIENT_ID" : os.getenv('BNI_VA_CREDIT_CLIENT_ID') or "99098",
    "VA_PREFIX"        : os.getenv('BNI_VA_PREFIX') or '988',
    "VA_LENGTH"        : 16,
    "BILLING"          : "createbilling",
    "CARDLESS"         : "createdebitcardless",
    "UPDATE"           : "updatebilling",
    "INQUIRY"          : "inquirybilling",
    "BILLING_TYPE"     : {
        "DEPOSIT"  : "o",
        "WITHDRAW" : "j"
    },
}

# BNI OPG CONFIG
BNI_OPG = {
    "MASTER_ACCOUNT": os.getenv('BNI_MASTER_ACCOUNT') or "0115476117",
    "BASE_URL"      : os.getenv('BNI_OPG_URL') or "https://apidev.bni.co.id",
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
