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
from app.api.utility.utils import Notif
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

        # debit (-) we increase balance
        debit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            notes=notes
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
        # send notification here
        notif_status = Notif().send({
            "wallet_id"        : str(wallet.id),
            "amount"           : amount,
            "transaction_type" : flag,
            "notes"            : notes
        })
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

        # credit (+) we increase balance
        credit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            notes=notes
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
        # send notification here
        notif_status = Notif().send({
            "wallet_id"        : str(wallet.id),
            "amount"           : amount,
            "transaction_type" : flag,
            "notes"            : notes
        })
        return credit_transaction
    #end def
#end class
