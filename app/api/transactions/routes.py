"""
    Transaction Routes
    _______________
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods
#pylint: disable=no-name-in-module

from flask_restplus import Resource
from marshmallow import ValidationError

from app.api.transactions import api
#serializer
#from app.api.serializer import *
# request schema
#from app.api.request_schema import *
# services
from app.api.transactions.modules.transaction_services import TransactionServices
# authentication
from app.api.auth.decorator import admin_required
# exceptions
#from app.api.error.http import *
# configuration
from app.config import config

class BaseRoutes(Resource):
    """ base routes class """
    error_response = config.Config.ERROR_CONFIG

@api.route('/refund/<string:transaction_id>')
class RefundTransactionRoutes(BaseRoutes):
    """
        Transaction Refund
        api/v1/transactions/refund/<transaction_id>
    """
    @admin_required
    def delete(self, transaction_id):
        """ endpoint for refunding a transaction """
        response = TransactionServices(transaction_id=transaction_id).refund()
        return response
    #end def
#end class
