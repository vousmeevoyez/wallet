"""
    Callback Services
    _________________
    This is module to process business logic from routes and return API
    response
"""
from sqlalchemy.exc import IntegrityError

from app.api import db
from app.api.models import *

from app.config import config

from app.api.wallet.modules.transfer_services import TransferServices

TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
WALLET_CONFIG = config.Config.WALLET_CONFIG
LOGGING_CONFIG = config.Config.LOGGING_CONFIG

class CallbackServices:
    """ Callback Services Class to handle all callback process here"""

    def __init__(self, virtual_account, trx_id):
        virtual_account = VirtualAccount.query.filter_by(id=virtual_account,
                                                         trx_id=trx_id).first()
        if virtual_account is None:
            raise VaNotFoundError

        self.virtual_account = virtual_account
    #end def

    def deposit(self, params):
        """
            Function to Deposit Money from Callback
            args:
                params -- parameter
        """
        payment_amount = params["payment_amount"]
        reference_number = params["payment_ntb"]
        payment_channel_key = params["payment_channel_key"]

        payment_channel = PaymentChannel.query.filter_by(key=payment_channel_key).first()

        # create payment
        payment_payload = {
            "channel_id"    : payment_channel.id,
            "source_account": self.virtual_account.id,
            "to"            : self.virtual_account.wallet_id,
            "ref_number"    : reference_number,
            "amount"        : payment_amount,
            "payment_type"  : True # Credit
        }
        payment_id = TransferServices.create_payment(payment_payload)

        # CREATE MASTER TRANSACTION
        master_transaction = MasterTransaction(
            source=self.virtual_account.id,
            destination=self.virtual_account.wallet_id,
            amount=payment_amount
        )

        # record and increase balance here
        wallet = self.virtual_account.wallet
        amount = payment_amount
        credit_transaction = TransferServices.credit_transaction(wallet,
                                                                 payment_id,
                                                                 amount,
                                                                 "TOP_UP")
        master_transaction.credit_transaction_id = credit_transaction.id
        master_transaction.debit_transaction_id = None

        try:
            db.session.add(master_transaction)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        #end def

        response = {
            "status" : "000"
        }
        return response
    #end def

    def withdraw(self, params):
        """
            Function to Withdraw Money from Callback
            args:
                params -- parameter
        """
        payment_amount = abs(params["payment_amount"])
        reference_number = params["payment_ntb"]
        payment_channel_key = params["payment_channel_key"]

        payment_channel = PaymentChannel.query.filter_by(key=payment_channel_key).first()

        # create payment
        payment_payload = {
            "channel_id"    : payment_channel.id,
            "source_account": self.virtual_account.id,
            "to"            : self.virtual_account.wallet_id,
            "ref_number"    : reference_number,
            "amount"        : payment_amount,
            "payment_type"  : False# Credit
        }
        payment_id = TransferServices.create_payment(payment_payload)

        # CREATE MASTER TRANSACTION
        master_transaction = MasterTransaction(
            source=self.virtual_account.id,
            destination=self.virtual_account.wallet_id,
            amount=payment_amount
        )

        # record and increase balance here
        wallet = self.virtual_account.wallet
        amount = payment_amount
        debit_transaction = TransferServices.debit_transaction(wallet,
                                                               payment_id,
                                                               amount,
                                                               "WITHDRAW")
        master_transaction.debit_transaction_id = debit_transaction.id
        master_transaction.credit_transaction_id = None

        try:
            db.session.add(master_transaction)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        #end def
        response = {
            "status" : "000"
        }
        return response
    #end def
#end class
