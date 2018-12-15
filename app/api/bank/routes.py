from flask              import request
from flask_restplus     import Resource

from app.api                import db
from app.api.bank           import api
from app.api.serializer     import BankSchema

from app.api.authentication.decorator import token_required, admin_required

from app.api.bank.modules   import bank

from app.api.errors import bad_request, internal_error, request_not_found

@api.route("/")
class BankRoutes(Resource):
    def get(self):
        response = bank.BankController().get_banks({})
        return response
    #end def
#end class
