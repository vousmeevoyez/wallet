"""
    Transfer Services
    _________________
    this is module that serve request from wallet transfer :w
    routes
"""
#pylint: disable=no-self-use
#pylint: disable=import-error
#pylint: disable=bad-whitespace
#pylint: disable=invalid-name
from sqlalchemy.exc import IntegrityError

from app.api import db
#models
from app.api.models import *
# core
from app.api.wallets.modules.wallet_core import WalletCore
from app.api.wallets.modules.transaction_core import TransactionCore
# exceptions
from app.api.error.http import *
#http response
from app.api.http_response import *
# serializer
from app.api.serializer import UserSchema
# utility
from app.api.utility.utils import validate_uuid
# task
from task.bank.tasks import BankTask

class TransferServices(WalletCore):
    """ Transfer Services"""

    def calculate_transfer_fee(self, destination, method=None):
        """ calculate transfer fee based on method and destination"""
        transfer_fee = 0

        bank_account = BankAccount.query.filter_by(
            id=validate_uuid(destination)
        ).first()
        if bank_account:
            if bank_account.bank.code != "009":
                transfer_fee = self.wallet_config["TRANSFER_FEE"][method]

        return transfer_fee

    def internal_transfer(self, params):
        """ method to transfer money internally"""
        amount = params["amount"]
        transfer_notes = params["notes"]
        transfer_types = params["types"] or "TRANSFER_IN"

        if float(amount) > float(self.source.balance):
            raise UnprocessableEntity(self.error_response["INSUFFICIENT_BALANCE"]["TITLE"],
                                      self.error_response["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        debit_trx = TransactionCore().process_transaction(
            source=self.source,
            destination=self.destination,
            amount=-amount,
            payment_type=False,
            transfer_types=transfer_types,
            transfer_notes=transfer_notes
        )

        destination_transfer_types = "RECEIVE_TRANSFER"
        if transfer_types == "PAYROLL":
            destination_transfer_types = "RECEIVE_PAYROLL"
        # end if

        credit_trx = TransactionCore().process_transaction(
            source=self.source,
            destination=self.destination,
            amount=amount,
            payment_type=True,
            transfer_types=destination_transfer_types,
            transfer_notes=transfer_notes
        )

        # link debit and credit
        debit_trx.transaction_link_id = credit_trx.id
        credit_trx.transaction_link_id = debit_trx.id
        db.session.commit()

        return accepted({"id" : str(debit_trx.id)})
    #end def

    def external_transfer(self, params, flag="TRANSFER_OUT"):
        """ method to transfer money externally"""
        bank_account_id = params["destination"]
        amount = params["amount"]
        transfer_notes = params["notes"]

        # calculate transfer fee here
        # for now only online
        transfer_fee = self.calculate_transfer_fee(bank_account_id, "ONLINE")

        if float(amount) + float(transfer_fee) > float(self.source.balance):
            raise UnprocessableEntity(self.error_response["INSUFFICIENT_BALANCE"]["TITLE"],
                                      self.error_response["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(
            id=validate_uuid(bank_account_id)
        ).first()
        if bank_account is None:
            raise RequestNotFound(self.error_response["BANK_ACC_NOT_FOUND"]["TITLE"],
                                  self.error_response["BANK_ACC_NOT_FOUND"]["MESSAGE"])
        #end if

        bank_transfer_trx = TransactionCore().process_transaction(
            source=self.source,
            destination=bank_account.account_no,
            amount=-amount,
            payment_type=False,
            transfer_types=flag,
            transfer_notes=transfer_notes
        )

        # create fee payment if transfer fee > 0
        if transfer_fee > 0:
            fee_trx = TransactionCore().process_transaction(
                source=self.source,
                destination="N/A",
                amount=-transfer_fee,
                payment_type=False,
                transfer_types="TRANSFER_FEE",
                transfer_notes=transfer_notes
            )
            # link bank and transaction fee
            bank_transfer_trx.transaction_link_id = fee_trx.id
            fee_trx.transaction_link_id = bank_transfer_trx.id
            db.session.commit()
        # end if

        # send queue here
        result = BankTask().bank_transfer.delay(
            bank_transfer_trx.payment.id
        )
        return accepted({"id": str(bank_transfer_trx.id)})
    #end def

    def checkout(self, phone_ext, phone_number):
        """
            Checkout Transfer
            exchange phone number and return wallet available for that users
        """
        user = User.query.filter_by(phone_ext=phone_ext,
                                    phone_number=phone_number).first()
        if user is None:
            raise RequestNotFound(self.error_response["USER_NOT_FOUND"]["TITLE"],
                                  self.error_response["USER_NOT_FOUND"]["MESSAGE"])
        #end if

        # serialize
        user_info = UserSchema(
            only=('name', 'msisdn','wallets.id', 'wallets.status')
        ).dump(user).data
        return ok(user_info)
    #end def

    ################################## PATCH ############################################
    def checkout2(self, phone_ext, phone_number):
        """
            Checkout Transfer
            exchange phone number and return wallet available for that users
        """
        user = User.query.filter_by(phone_ext=phone_ext,
                                    phone_number=phone_number).first()
        if user is None:
            raise RequestNotFound(self.error_response["USER_NOT_FOUND"]["TITLE"],
                                  self.error_response["USER_NOT_FOUND"]["MESSAGE"])
        #end if

        # serialize
        user_info = UserSchema().dump(user).data
        return ok(user_info)
    #end def
#end class
