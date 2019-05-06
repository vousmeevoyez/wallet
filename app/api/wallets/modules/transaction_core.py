"""
    Transfer Core
    _________________
"""
#pylint: disable=no-self-use
#pylint: disable=import-error
#pylint: disable=bad-whitespace
#pylint: disable=invalid-name
#pylint: disable=no-name-in-module
#pylint: disable=no-member
from sqlalchemy.exc import IntegrityError
from app.api import db
#models
from app.api.models import Transaction
from app.api.models import TransactionType
from app.api.models import Payment
from app.api.models import TransactionNote
# exceptions
from app.api.error.http import UnprocessableEntity
# configuration
from app.config import config
# utility
from app.api.utility.utils import Notif
# task
from task.transaction.tasks import TransactionTask

class TransactionError(Exception):
    """ raised when something occured on creating transaction """
    def __init__(self, original_exception):
        super().__init__(original_exception)
        self.original_exception = original_exception

class TransactionCore:
    """ Transfer Services"""

    error_response = config.Config.ERROR_CONFIG

    @staticmethod
    def debit_transaction(wallet, payment_id, amount, flag,
                          transfer_notes=None):
        """ create debit transaction """
        amount = -amount

        # fetch transaction type from db
        transaction_type = TransactionType.query.filter_by(key=flag).first()

        if transfer_notes is None:
            transfer_notes = TransactionNote.query.filter_by(key=flag).first()
            notes = transfer_notes.notes.format(str(amount))
        else:
            notes = transfer_notes
        #end if

        # debit (-) we increase balance
        debit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type_id=transaction_type.id,
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
        result = TransactionTask().transfer.apply_async(args=[payment_id], queue="transaction")
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
        # fetch transaction type from db
        transaction_type = TransactionType.query.filter_by(key=flag).first()

        if transfer_notes is None:
            transfer_notes = TransactionNote.query.filter_by(key=flag).first()
            notes = transfer_notes.notes.format(str(amount))
        else:
            notes = transfer_notes
        #end if

        # credit (+) we increase balance
        credit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type_id=transaction_type.id,
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
        result = TransactionTask().transfer.apply_async(args=[payment_id], queue="transaction")
        # send notification here
        notif_status = Notif().send({
            "wallet_id"        : str(wallet.id),
            "amount"           : amount,
            "transaction_type" : flag,
            "notes"            : notes
        })
        return credit_transaction
    #end def

    @staticmethod
    def create_payment(params):
        """
            Function to create payment
            args:
                params --
        """
        # build payment object
        payment = Payment(**params)
        try:
            db.session.add(payment)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            return None
        return payment.id
    #end def

    def process_transaction(self, source, destination, amount, payment_type,
                            transfer_types, transfer_notes=None,
                            channel_id=None, reference_number=None):
        """ method that wrap debit & credit transaction process """
        # if destination is bank account
        if hasattr(source, "id"):
            source_account = source.id
        else:
            source_account = source

        if hasattr(destination, "id"):
            to = destination.id
        else:
            to = destination

        # create payment
        payment = {
            "payment_type"  : payment_type,
            "source_account": source_account,
            "to"            : to,
            "amount"        : amount,
            "channel_id"    : channel_id, # payment channel id,
            "ref_number"    : reference_number
        }

        payment_id = TransactionCore.create_payment(payment)
        if payment_id is None:
            raise UnprocessableEntity(self.error_response["DUPLICATE_PAYMENT"]["TITLE"],
                                      self.error_response["DUPLICATE_PAYMENT"]["MESSAGE"])
        # end if

        if payment_type:
            try:
                transaction = TransactionCore.credit_transaction(
                    destination, payment_id, abs(amount),
                    transfer_types, transfer_notes
                )
            except TransactionError as error:
                print(error)
                db.session.rollback()
                raise UnprocessableEntity(self.error_response["TRANSFER_FAILED"]["TITLE"],
                                          self.error_response["TRANSFER_FAILED"]["MESSAGE"])
            # end try
        else:
            # debit transaction
            try:
                transaction = TransactionCore.debit_transaction(
                    source, payment_id, abs(amount),
                    transfer_types, transfer_notes
                )
            except TransactionError as error:
                print(error)
                db.session.rollback()
                # still commit the master transaction
                raise UnprocessableEntity(self.error_response["TRANSFER_FAILED"]["TITLE"],
                                          self.error_response["TRANSFER_FAILED"]["MESSAGE"])
        # end if
        return transaction
    # end def
#end class
