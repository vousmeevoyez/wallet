"""
    Flask App
    ______________________
    Package Initialization
"""
from flask  import Flask
from flask  import request
from flask  import current_app
from flask  import jsonify

from celery import Celery

from flask_sqlalchemy   import SQLAlchemy
from flask_marshmallow  import Marshmallow

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app.config import config

db = SQLAlchemy()
ma = Marshmallow()
sentry = sentry_sdk
celery = Celery(__name__, broker=config.Config.CELERY_BROKER_URL)

def create_app(config_name):
    """
    Create flask instance using application factory pattern

    args :
        config_name -- Configuration key used (DEV/PROD/TESTING)
    """
    app = Flask(__name__)
    app.config.from_object(config.CONFIG_BY_NAME[config_name])

    db.init_app(app)
    ma.init_app(app)
    celery.conf.update(app.config) # update celery with flask application configuration


    #if not app.testing and not app.debug:
    sentry_sdk.init(
        dsn="https://c864361a612b47a3827e2c5b3280a727@sentry.io/1385947",
        integrations=[FlaskIntegration()]
    )
    
    return app
