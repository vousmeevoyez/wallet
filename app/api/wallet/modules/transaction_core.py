"""
    Transfer Core
    _________________
    Core Transaction Services
"""
#pylint: disable=no-self-use
#pylint: disable=import-error
#pylint: disable=bad-whitespace
#pylint: disable=invalid-name
from sqlalchemy.exc import IntegrityError

from app.api import db
#models
from app.api.models import *
# exceptions
from app.api.error.http import *
#ttp errors
from app.api.http_response import accepted
from app.api.http_response import no_content
# configuration
from app.config import config
# utility
from app.api.utility.utils import validate_uuid
# task
from task.transaction.tasks import TransactionTask

TRANSACTION_CONFIG = config.Config.TRANSACTION_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
ERROR_CONFIG = config.Config.ERROR_CONFIG

class TransactionError(Exception):
    """ raised when something occured on creating transaction """
    def __init__(self, original_exception):
        super().__init__(original_exception)
        self.original_exception = original_exception

class TransactionCore:
    """ Transfer Services"""
    @staticmethod
    def debit_transaction(wallet, payment_id, amount, flag,
                          transfer_notes=None):

        amount = -amount

        # fetch transaction type from config
        transaction_type = TRANSACTION_CONFIG["TYPES"][flag]

        if transfer_notes is None:
            notes = TRANSACTION_NOTES["SEND_TRANSFER"].format(str(amount))
        else:
            notes = transfer_notes
        #end if

        # get latest wallet record here
        wallet = Wallet.query.filter_by(id=wallet.id).first()

        # debit (-) we increase balance
        debit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            notes=notes,
            balance=wallet.balance+amount
        )
        try:
            db.session.add(debit_transaction)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise TransactionError(error)
        #end try
        # should send queue here
        result = TransactionTask().transfer.delay(payment_id)
        return debit_transaction
    #end def

    @staticmethod
    def credit_transaction(wallet, payment_id, amount, flag,
                           transfer_notes=None):
        """ create credit transaction and add balance """
        transaction_type = TRANSACTION_CONFIG["TYPES"][flag]

        if transfer_notes is None:
            notes = TRANSACTION_NOTES["RECEIVE_TRANSFER"].format(str(amount))
        else:
            notes = transfer_notes
        #end if

        # get latest wallet record here
        wallet = Wallet.query.filter_by(id=wallet.id).first()

        # credit (+) we increase balance
        credit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            notes=notes,
            balance=wallet.balance+amount
        )
        try:
            db.session.add(credit_transaction)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise TransactionError(error)
        #end try
        # send queue here
        result = TransactionTask().transfer.delay(payment_id)
        return credit_transaction
    #end def
#end class
