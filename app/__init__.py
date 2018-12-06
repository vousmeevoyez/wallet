from flask_restplus import Api

from flask import Blueprint

from app.api.user           import api as user_ns
from app.api.authentication import api as auth_ns
from app.api.wallet         import api as wallet_ns
from app.api.bank           import api as bank_ns
from app.api.callback       import api as callback_ns

blueprint = Blueprint("api", __name__)

api = Api(blueprint,
            version="1.0",
         )

api.add_namespace(user_ns,   path="/users")
api.add_namespace(auth_ns,   path="/auth")
api.add_namespace(wallet_ns, path="/wallets")
api.add_namespace(callback_ns, path="/callback")
api.add_namespace(bank_ns)
