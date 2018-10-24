from flask              import Flask, request, current_app
from flask_sqlalchemy   import SQLAlchemy
from flask_migrate      import Migrate
from flask_marshmallow  import Marshmallow

from app.config import config

db      = SQLAlchemy()
migrate = Migrate()
ma      = Marshmallow()

def create_app(config_class=config.Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app,db)
    ma.init_app(app)

    from app.access_key import bp as access_key_bp
    app.register_blueprint(access_key_bp, url_prefix="/access_key")

    from app.wallet     import bp as wallet_bp
    app.register_blueprint(wallet_bp, url_prefix="/wallet")

    from app.transfer   import bp as transfer_bp
    app.register_blueprint(transfer_bp, url_prefix="/transfer")

    return app

from app import models, errors, serializer, validator
