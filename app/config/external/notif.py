import os

HR_NOTIF = {
    "BASE_URL": os.getenv("NOTIF_SERVICES_BASE_URL")
    or "http://147.139.134.250:8000/wallet/api/send-wallet-notification"
}
