from flask              import Flask, request, current_app
from flask_sqlalchemy   import SQLAlchemy
from flask_marshmallow  import Marshmallow

from app.api.config import config

db      = SQLAlchemy()
ma      = Marshmallow()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.config_by_name[config_name])

    db.init_app(app)
    ma.init_app(app)

    return app

