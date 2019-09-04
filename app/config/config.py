"""
    Configuration
    _______________
    This is module for storing all configuration for various environments
"""
# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """ This is base class for configuration """
    DEBUG = False
    BUNDLE_ERRORS = True #configuration key for flask-restplus to enable bundle erors

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # FLASK RESTPLUS
    ERROR_INCLUDE_MESSAGE = False

    DATABASE = {
        "DRIVER"   : os.getenv('DB_DRIVER') or "postgresql://", # sqlite // postgresql // mysql
        "USERNAME" : os.getenv('DB_USERNAME') or "modana",
        "PASSWORD" : os.getenv('DB_PASSWORD') or "passsword",
        "HOST_NAME": os.getenv('DB_HOSTNAME') or "localhost",
        "DB_NAME"  : os.getenv('DB_NAME') or "db_wallet",
    }

    SENTRY_CONFIG = {}

    CELERY_BROKER_URL = os.getenv("BROKER_URL") or \
    'amqp://guest:guest@localhost:5672'
    # REGISTER ALL KNOWN CELERY TASK HERE
    CELERY_IMPORTS = (
        "task.bank.tasks", "task.transaction.tasks", "task.payment.tasks", "task.utility.tasks"
    )
    CELERY_TASK_DEFAULT_QUEUE = "default"
    # REGISTER ALL KNOWN QUEUES HERE
    CELERY_QUEUES = {
        "default" : {
            "exchange" : "default",
            "binding_key" : "default"
        },
        "payment" : {
            "exchange" : "payment",
            "binding_key" : "payment"
        },
        "bank" : {
            "exchange" : "bank",
            "binding_key" : "bank"
        },
        "transaction" : {
            "exchange" : "transaction",
            "binding_key" : "transaction"
        },
        "utility" : {
            "exchange" : "utility",
            "binding_key" : "utility"
        }
    }
    CELERY_TRACK_STARTED = True

    # APSCHEDULER JOBSTORE
    APSCHEDULER_JOBSTORE_URI = "sqlite:///jobs.sqlite"
#end class


class DevelopmentConfig(Config):
    """ This is class for development configuration """
    DEBUG = True

    DATABASE = Config.DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
            DATABASE["DRIVER"] + DATABASE["USERNAME"] + ":" + \
            DATABASE["PASSWORD"] + "@" + DATABASE["HOST_NAME"] + "/" + \
            DATABASE["DB_NAME"] + "_dev"

    CELERY_RESULT_BACKEND = "db+" + SQLALCHEMY_DATABASE_URI

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

    CELERY_RESULT_BACKEND = "db+" + SQLALCHEMY_DATABASE_URI

    #CELERY_TASK_ALWAYS_EAGER = True

    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BACKGROUND_PAYMENT_CONFIG = {
        "DAY" : os.getenv("PAYMENT_IN_DAY") or 10, # minutes
        "COUNTDOWN"  : os.getenv("PAYMENT_COUNTDOWN") or 1, # minutes
        "EXPIRES" : os.getenv("PAYMENT_EXPIRES") or 1728000 # SECONDS
    }
#end class


class ProductionConfig(Config):
    """ This is class for production configuration """
    DEBUG = False

    DATABASE = Config.DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
            DATABASE["DRIVER"] + DATABASE["USERNAME"] + ":" + \
            DATABASE["PASSWORD"] + "@" + DATABASE["HOST_NAME"] + "/" + \
            DATABASE["DB_NAME"] + "_prod"

    CELERY_RESULT_BACKEND = "db+" + SQLALCHEMY_DATABASE_URI

    PRESERVE_CONTEXT_ON_EXCEPTION = False

    SENTRY_CONFIG = Config.SENTRY_CONFIG
    SENTRY_CONFIG["dsn"] = os.environ.get("SENTRY_DSN")
#end class


CONFIG_BY_NAME = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
