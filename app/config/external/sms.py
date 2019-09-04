import os

WAVECELL = {
    "BASE_URL"   : os.getenv('SMS_SERVICES_BASE_URL') or \
    "https://api.wavecell.com/sms/v1/Modana_OTP/single",
    "API_KEY"    : os.getenv('SMS_SERVICES_API_KEY') or \
    "7hH72ACD8DA6EED4DD985D4489A034",
    "FROM"       : "MODANA",
}

TEMPLATES = {
    "FORGOT_PIN" : "Kode verifikasi keamanan. PENTING : demi keamanan akun Anda, mohon tidak memberitahukan kepada pihak manapun.Kode Rahasia : {}"
}
