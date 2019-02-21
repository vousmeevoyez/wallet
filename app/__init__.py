"""
    Package Initialization
    _______________________
    this module aggregate all wallet modules
"""
from flask_restplus import Api

from flask import Blueprint

from app.api import sentry

from app.api.user           import api as user_ns
from app.api.authentication import api as auth_ns
from app.api.wallet         import api as wallet_ns
from app.api.bank           import api as bank_ns
from app.api.callback       import api as callback_ns
from app.api.log            import api as log_ns
from app.api.utility        import api as utility


blueprint = Blueprint("api", __name__)

class CustomApi(Api):
    """ Custom API Classs """
    def handle_error(self, e):
        """ Overrides the handle_error() method of the Api and adds custom error handling
        :param e: error object
        """
        code = getattr(e, 'code', 500)  # Gets code or defaults to 500
        message = getattr(e, 'message', 'INTERNAL_SERVER_ERROR')
        to_dict = getattr(e, 'to_dict', None)

        if code == 500:
            # capture error and send to sentry
            sentry.captureException(e)
            data = {'error': message}

        # handle request schema error from reqparse
        if code == 400:
            response = getattr(e, 'response', True)
            if response is None:
                # build error response
                data = {
                    "error" : "MISSING_PARAMETER",
                    "message" : e.data['message'],
                    "details" : e.data['errors']
                }

        if to_dict:
            data = to_dict()    

        return self.make_response(data, code)

api = CustomApi(blueprint,
                catch_all_404s=True,
                version="1.0",
                ui=False,
                contact="kelvin@modana.id"
                )

api.add_namespace(user_ns, path="/users")
api.add_namespace(auth_ns, path="/auth")
api.add_namespace(wallet_ns, path="/wallets")
api.add_namespace(callback_ns, path="/callback")
api.add_namespace(bank_ns, path="/banks")
api.add_namespace(log_ns, path="/logs")
api.add_namespace(utility)