from flask              import Flask, request, current_app
from flask_sqlalchemy   import SQLAlchemy
from flask_migrate      import Migrate
from flask_marshmallow  import Marshmallow
from flask_jwt_extended import JWTManager

from app.config import config

db      = SQLAlchemy()
migrate = Migrate()
ma      = Marshmallow()
jwt     = JWTManager()

def create_app(config_class=config.Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app,db)
    ma.init_app(app)
    jwt.init_app(app)

    from app.authentication import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.access_key import bp as access_key_bp
    app.register_blueprint(access_key_bp, url_prefix="/access_key")

    from app.wallet     import bp as wallet_bp
    app.register_blueprint(wallet_bp, url_prefix="/wallet")

    from app.transfer   import bp as transfer_bp
    app.register_blueprint(transfer_bp, url_prefix="/transfer")

    from app.bank       import bp as bank_bp
    app.register_blueprint(bank_bp)

    from app.withdraw   import bp as withdraw_bp
    app.register_blueprint(withdraw_bp, url_prefix="/withdraw")

    from app.user       import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/user")

    from app.callback   import bp as callback_bp
    app.register_blueprint(callback_bp, url_prefix="/callback")

    return app

from app import models, errors, serializer
