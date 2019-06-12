"""
    Transaction Services
    ________________
    This is module that serve everything related to Transaction
"""
#pylint: disable=bad-whitespace
#pylint: disable=no-self-use
#pylint: disable=import-error
#pylint: disable=no-name-in-module
#pylint: disable=singleton-comparison
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from app.api import db
# helper
from app.api.utility.utils import validate_uuid
# models
from app.api.models import Wallet, Transaction, Payment
# serializer
from app.api.serializer import TransactionSchema
# core
from app.api.wallets.modules.transaction_core import TransactionCore
# config
from app.config import config
# http error
from app.api.http_response import ok, accepted
# exception
from app.api.error.http import UnprocessableEntity, RequestNotFound

class TransactionServices:
    """ Transaction Services Class"""

    error_response = config.Config.ERROR_CONFIG

    def __init__(self, wallet_id=None, transaction_id=None):
        # only look up in db when source is set
        if wallet_id is not None:
            wallet_record = Wallet.query.filter_by(id=validate_uuid(wallet_id)).first()
            if wallet_record is None:
                raise RequestNotFound(self.error_response["WALLET_NOT_FOUND"]["TITLE"],
                                      self.error_response["WALLET_NOT_FOUND"]["MESSAGE"])
            #end if
            self.wallet = wallet_record
        # end if

        if transaction_id is not None:
            transaction_record = Transaction.query.filter_by(
                id=validate_uuid(transaction_id)
            ).first()
            if transaction_record is None:
                raise RequestNotFound(self.error_response["TRANSACTION_NOT_FOUND"]["TITLE"],
                                      self.error_response["TRANSACTION_NOT_FOUND"]["MESSAGE"])
            #end if
            self.transaction = transaction_record
        # end if
    #end def

    def history(self, params):
        """
            function to check wallet transaction history
            args :
                params -- parameter
        """
        start_date = params["start_date"]
        end_date = params["end_date"]
        transaction_type = params["flag"]

        conditions = [Transaction.wallet_id == self.wallet.id]
        # filter by transaction type
        if transaction_type == "IN":
            conditions.append(Payment.payment_type == True)
        elif transaction_type == "OUT":
            conditions.append(Payment.payment_type == False)
        #end if

        # filter by transaction date
        if start_date is not None and end_date is not None:
            start_date = datetime.strptime(start_date, "%Y/%m/%d")
            end_date = datetime.strptime(end_date, "%Y/%m/%d")
            end_date = end_date + timedelta(hours=23, minutes=59)

            conditions.append(Transaction.created_at.between(start_date, \
                                                                 end_date))
        #end if
        wallet_response = Transaction.query.join(Payment,
                                                 Transaction.payment_id == \
                                                 Payment.id,
                                                 ).filter(*conditions)
        transaction_history = TransactionSchema(many=True,
                                                exclude=["payment_details","wallet_id"]).\
                                                dump(wallet_response).data
        return ok(transaction_history)
    #end def

    def history_details(self):
        """
            function to check wallet transaction details
            args :
                wallet_id --
                transaction_id --
        """
        transaction_details = TransactionSchema().dump(self.transaction).data
        return ok(transaction_details)
    #end def

    def refund(self):
        """ method to refund a transaction """
        # make sure the transaction is not refunded yet == CANCELLED
        if self.transaction.payment.status == 2 :
            raise UnprocessableEntity(self.error_response["TRANSACTION_REFUNDED"]["TITLE"],
                                      self.error_response["TRANSACTION_REFUNDED"]["MESSAGE"])

        # prevent refund a refund transaction!
        if self.transaction.transaction_type.key == "REFUND":
            raise UnprocessableEntity(self.error_response["INVALID_REFUND"]["TITLE"],
                                      self.error_response["INVALID_REFUND"]["MESSAGE"])

        # populates refund transaction
        refunds = []
        # append current object
        refunds.append(self.transaction)
        # if transaction link is existed append it too
        if self.transaction.transaction_link is not None:
            refunds.append(self.transaction.transaction_link)
        # end if

        transactions = []
        for refund in refunds:
            # fetch all information needed
            source = refund.payment.to
            destination = refund.payment.source_account

            # only look up object when it is not a bank account
            if not source.isdigit() and source != "N/A":
                source = Wallet.query.filter_by(id=validate_uuid(source)).first()

            # only look up object when it is not a bank account
            if not destination.isdigit():
                destination = Wallet.query.filter_by(id=validate_uuid(destination)).first()

            if refund.payment.payment_type is False:
                refunded_amount = abs(refund.payment.amount)

                transaction = TransactionCore().process_transaction(
                    source=source,
                    destination=destination,
                    amount=refunded_amount,
                    payment_type=True,
                    transfer_types="REFUND"
                )
            else:
                refunded_amount = -refund.payment.amount

                transaction = TransactionCore().process_transaction(
                    source=source,
                    destination=destination,
                    amount=refunded_amount,
                    payment_type=False,
                    transfer_types="REFUND"
                )
            # end if
            # update payment status to refunded
            refund.payment.status = 2
            db.session.commit()
            # append
            transactions.append({ "id" : str(transaction.id) })
        # end for
        return accepted(transactions)
#end class
