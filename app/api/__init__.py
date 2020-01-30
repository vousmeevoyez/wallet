"""
    Flask App
    ______________________
    Package Initialization
"""
# pylint: disable=import-error
# pylint: disable=invalid-name

from flask import Flask

from celery import Celery

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import config, logging

db = SQLAlchemy()
ma = Marshmallow()
sentry = sentry_sdk
celery = Celery(__name__, broker=config.Config.CELERY_BROKER_URL)
# start scheduler
scheduler = BackgroundScheduler()
scheduler.start()


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
    celery.conf.update(app.config)  # update celery with flask application configuration

    if not app.testing and not app.debug:
        sentry_sdk.init(
            integrations=[
                FlaskIntegration(),
                CeleryIntegration(),
                SqlalchemyIntegration(),
            ]
        )
    return app
