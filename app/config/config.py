import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "S3cret"
    # SQL ALCHEMY CONFIG
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # BNI E-COLLECTION CONFIG
    BNI_ECOLLECTION_CONFIG = {
        "BASE_URL_DEV"  : "https://apibeta.bni-ecollection.com/",
        "BASE_URL_PROD" : "https://apibeta.bni-ecollection.com/",
        "SECRET_KEY"    : "8eafc8687722fdd0ef78942309fcd983",
        "CLIENT_ID"     : "99099",
        "BILLING_TYPE"  : "J",
    }

    # BNI OPG CONFIG
    BNI_OPG_CONFIG = {
        "BASE_URL_DEV"  : "https://apibeta.bni-ecollection.com/",
        "BASE_URL_PROD" : "https://apibeta.bni-ecollection.com/",
        "SECRET_KEY"    : "8eafc8687722fdd0ef78942309fcd983",
        "CLIENT_ID"     : "99099",
        "BILLING_TYPE"  : "J",
    }
