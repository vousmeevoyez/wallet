"""
    Wallet Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods

from flask_restplus import Resource
from marshmallow import ValidationError

from app.api.transactions import api
#serializer
from app.api.serializer import *
# request schema
from app.api.request_schema import *
# services
from app.api.transactions.modules.transaction_services import TransactionServices
# authentication
from app.api.auth.decorator import token_required
from app.api.auth.decorator import get_token_payload
from app.api.auth.decorator import admin_required
# exceptions
from app.api.error.http import *
# configuration
from app.config import config

class BaseRoutes(Resource):
    error_response = config.Config.ERROR_CONFIG

'''
@api.route('/<string:wallet_id>/transactions')
class WalletTransactionRoutes(BaseRoutes):
    """
        Wallet Transaction Routes
        api/v1/<wallet_id>/transactions
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/transactions
            return wallet transaction list
        """
        request_data = WalletTransactionRequestSchema.parser.parse_args(strict=True)
        try:
            wallet = WalletTransactionSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)

        response = WalletServices(wallet_id).history(request_data)
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/transactions/<transaction_id>')
class WalletTransactionDetailsRoutes(BaseRoutes):
    """
        Wallet Transaction Details Routes
        api/v1/<wallet_id>/transactions/<transaction_id>
    """
    @token_required
    def get(self, wallet_id, transaction_id):
        """
            handle GET method from
            api/v1/<wallet_id>/transactions/<transaction_id>
            return wallet transaction details
        """
        response = WalletServices(wallet_id).history_details(transaction_id)
        return response
    #end def
#end class
'''

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
