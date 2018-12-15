import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify

from app.api            import db
from app.api.models     import Bank
from app.api.serializer import BankSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class BankController:

    def __init__(self):
        pass
    #end def

    def get_banks(self, params):
        response = {}

        # only show active bank
        banks = Bank.query.filter_by(status=True).all()

        response["data"] = BankSchema(many=True).dump(banks).data
        return response
    #end def
#end class
