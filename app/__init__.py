"""
    Package Initialization
    _______________________
    this module aggregate all wallet modules
"""
from importlib import import_module
from flask_restplus import Api

from flask import Blueprint

from app.api import sentry

def register_blueprint(api):
    """ regist all module here"""
    for module in ("auth", "wallets", "users", "virtual_accounts",
                   "payment_plans", "plans", "callback", "banks", "logs", "utility", "transactions","schedulers"):
        namespace = import_module('app.api.{}'.format(module))
        api.add_namespace(namespace.api, path="/{}".format(module))

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

blueprint = Blueprint("api", __name__)
api = CustomApi(blueprint,
                catch_all_404s=True,
                version="1.0",
                ui=False,
                contact="kelvin@modana.id"
                )
# register all modules
register_blueprint(api)
