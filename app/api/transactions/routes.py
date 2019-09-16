"""
    Transaction Routes
    _______________
"""
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods
# pylint: disable=no-name-in-module

from app.api.core import Routes
from app.api.transactions import api

# services
from app.api.transactions.modules.transaction_services import TransactionServices

# authentication
from app.api.auth.decorator import admin_required


@api.route("/refund/<string:transaction_id>")
class RefundTransactionRoutes(Routes):
    """
        Transaction Refund
        api/v1/transactions/refund/<transaction_id>
    """

    @admin_required
    def delete(self, transaction_id):
        """ endpoint for refunding a transaction """
        response = TransactionServices(transaction_id=transaction_id).refund()
        return response

    # end def


# end class
