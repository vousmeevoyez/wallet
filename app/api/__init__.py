"""
    Flask App
    ______________________
    Package Initialization
"""
from flask              import Flask, request, current_app
from flask_sqlalchemy   import SQLAlchemy
from flask_marshmallow  import Marshmallow

from app.api.config import config

db = SQLAlchemy()
ma = Marshmallow()

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

    return app
