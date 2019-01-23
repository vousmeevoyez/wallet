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
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.api import db
#helper
from app.api.bank.handler import BankHandler
from app.api.common.helper import QR
#models
from app.api.models import Wallet
from app.api.models import Transaction
from app.api.models import Payment
from app.api.models import BankAccount
from app.api.models import MasterTransaction
# exceptions
from app.api.exception.wallet.exceptions import WalletNotFoundError
from app.api.exception.wallet.exceptions import WalletLockedError
from app.api.exception.wallet.exceptions import IncorrectPinError
from app.api.exception.wallet.exceptions import InsufficientBalanceError
from app.api.exception.wallet.exceptions import InvalidDestinationError
from app.api.exception.wallet.exceptions import TransactionError
from app.api.exception.wallet.exceptions import TransferError

from app.api.exception.common.exceptions import DecryptError
#ttp errors
from app.api.errors import bad_request
from app.api.errors import internal_error
# configuration
from app.api.config import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
RESPONSE_MSG      = config.Config.RESPONSE_MSG
WALLET_CONFIG     = config.Config.WALLET_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
BNI_OPG_CONFIG    = config.Config.BNI_OPG_CONFIG

class TransferServices:
    """ Transfer Services"""

    def _create_payment(self, params, session=None):
        """
            Function to create payment
            args:
                params --
                session -- optional
        """
        if session is None:
            session = db.session
        #end if
        session.begin(nested=True)

        source_account = params["source"]
        to             = params["destination"]
        amount         = params["amount"]
        payment_type   = params["payment_type"]

        # build payment object
        payment = Payment(
            source_account=source_account,
            to=to,
            amount=amount,
            payment_type=payment_type,
        )
        try:
            session.add(payment)
            session.commit()
        except IntegrityError as error:
            session.rollback()
        return payment.id
    #end def

    def qr_transfer(self, params):
        """
            Function to transfer between wallet using qr code
            args:
                params --
        """
        try:
            encrypted_payload = QR().read(params["qr_string"])
        except DecryptError:
            return bad_request("Invalid QR")
        #end try
        params["destination"] = encrypted_payload["wallet_id"]
        return self.internal_transfer(params)
    #end def

    def internal_transfer(self, params):
        """
            Function to transfer between wallet
            args:
                params --
        """
        response = {
            "data"   : "NONE"
        }

        try:
            self._do_transaction(params)
        except (WalletNotFoundError, WalletLockedError, IncorrectPinError,
                InsufficientBalanceError, InvalidDestinationError) as error:
            return bad_request(error.msg)
        except TransferError as error:
            return internal_error(error.msg)
        #end if

        response["data"] =\
        RESPONSE_MSG["SUCCESS"]["TRANSFER"].format(str(params["amount"]),\
                                                   str(params["source"]),\
                                                   str(params["destination"]))
        return response
    #end def

    def external_transfer(self, params):
        """
            Function to handle transfer to External System
        """
        response = {
            "data"   : "NONE"
        }

        # CREATE TRANSACTION SESSION
        try:
            session = db.session(autocommit=True)
        except InvalidRequestError:
            db.session.commit()
            session = db.session()
        #end try
        session.begin(subtransactions=True)

        transfer_response = self._do_ext_transaction(params, session)
        if transfer_response["status"] == "CLIENT_ERROR":
            return bad_request(transfer_response["data"])
        elif transfer_response["status"] == "SERVER_ERROR":
            return internal_error(transfer_response["data"])
        #end if

        session.commit()

        response["data"] = \
        RESPONSE_MSG["SUCCESS"]["TRANSFER"].format(str(params["amount"]),\
                                                   str(params["source"]),\
                                                   str(params["destination"]))
        return response
    #end def

    def _do_transaction(self, params, session=None):
        source      = params["source"     ]
        destination = params["destination"]
        amount      = params["amount"     ]
        pin         = params["pin"        ]

        if session is None:
            session = db.session
        #end if
        session.begin(nested=True)

        source_wallet = Wallet.query.filter_by(id=source).with_for_update().first()
        if source_wallet is None:
            raise WalletNotFoundError(source)
        #end if

        if source_wallet.is_unlocked() is False:
            raise WalletLockedError(source)
        #end if

        if source_wallet.check_pin(pin) is not True:
            raise IncorrectPinError
        #end if

        if float(amount) > float(source_wallet.balance):
            raise InsufficientBalanceError(source_wallet.balance, amount)
        #end if

        destination_wallet = \
        Wallet.query.filter_by(id=destination).\
                with_for_update().first()
        if destination_wallet is None:
            raise WalletNotFoundError(destination)
        #end if

        if destination_wallet.is_unlocked() is False:
            raise WalletLockedError(destination)
        #end if

        if destination_wallet == source_wallet:
            raise InvalidDestinationError
        #end if

        # create master transaction here that track every transaction
        master_transaction = MasterTransaction(
            source=source_wallet.id,
            destination=destination_wallet.id,
            amount=amount
        )
        try:
            session.add(master_transaction)
        except IntegrityError:
            session.rollback()
        #end def

        # create debit payment
        params["payment_type"] = False # debit
        debit_payment_id = self._create_payment(params, session)

        # debit transaction
        try:
            debit_trx = self._debit_transaction(source_wallet, debit_payment_id, amount,\
                                    "IN", session)
        except TransactionError as error:
            # flag as transaction CANCELED
            master_transaction.state = 3
            # still commit the master transaction
            raise TransferError(error)
        #end if

        # update to PENDING
        master_transaction.state = 1
        # append transaction id
        master_transaction.debit_transaction_id = debit_trx.id

        # create credit payment
        params["payment_type"] = True # credit
        credit_payment_id = self._create_payment(params, session)

        # credit transaction
        try:
            credit_trx = self._credit_transaction(destination_wallet, credit_payment_id,\
                                 amount, session)
        except TransactionError as error:
            master_transaction.state = 3
            raise TransferError(error)
        #end if

        # update to DONE
        master_transaction.state = 2
        # append transaction id
        master_transaction.credit_transaction_id = credit_trx.id

        session.commit()
    #end def

    def _do_ext_transaction(self, params, session=None):
        response = {
            "status" : "SUCCESS",
            "data"   : None
        }

        source          = params["source"]
        bank_account_id = params["destination"]
        amount          = params["amount"]
        pin             = params["pin"]

        if session is None:
            session = db.session
        #end if

        source_wallet = Wallet.query.filter_by(id=source).with_for_update().first()
        if source_wallet is None:
            raise WalletNotFoundError(source)
        #end if

        if source_wallet.is_unlocked() is False:
            raise WalletLockedError(source)
        #end if

        if source_wallet.check_pin(pin) is not True:
            raise IncorrectPinError
        #end if

        if float(amount) > float(source_wallet.balance):
            raise InsufficientBalanceError(source_wallet.balance, amount)
        #end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(id=bank_account_id).first()

        # get information needed for transfer
        payment_payload = {
            "amount"         : amount,
            "source_account" : BNI_OPG_CONFIG["MASTER_ACCOUNT"],
            "account_no"     : bank_account.account_no,
            "bank_code"      : bank_account.bank.code,
        }
        payment_response = BankHandler("BNI").dispatch("DIRECT_TRANSFER",
                                                       payment_payload)
        if payment_response["status"] != "SUCCESS":
            response["status"] = "SERVER_ERROR"
            response["data"] = RESPONSE_MSG["FAILED"]["TRANSFER_FAILED"]
            return response
        #end if

        # create debit payment
        params["payment_type"] = False # debit
        debit_payment_id = self._create_payment(params, session)

        # debit transaction
        try:
            self._debit_transaction(source_wallet, debit_payment_id, amount,\
                                    "OUT", session)
        except TransactionError as error:
            raise TransferError(error)
        #end if

        session.commit()
        return response
    #end def

    @staticmethod
    def _debit_transaction(wallet, payment_id, amount, flag, session=None):
        if session is None:
            session = db.session
        #end if
        session.begin(nested=True)

        amount = -float(amount)

        if flag == "IN":
            transaction_type = WALLET_CONFIG["IN_TRANSFER"]
        else:
            transaction_type = WALLET_CONFIG["OUT_TRANSFER"]
        #end if

        # deduct balance first
        wallet.add_balance(amount)

        # debit (-) we increase balance
        debit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            notes=TRANSACTION_NOTES["SEND_TRANSFER"].format(str(amount))
        )
        debit_transaction.generate_trx_id()

        try:
            session.add(debit_transaction)
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise TransactionError(error)
        #end try
        return debit_transaction
    #end def

    @staticmethod
    def _credit_transaction(wallet, payment_id, amount, session=None):
        if session is None:
            session = db.session
        #end if
        session.begin(nested=True)

        amount = float(amount)
        # credit (+) we increase balance
        credit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=WALLET_CONFIG["IN_TRANSFER"],
            notes=TRANSACTION_NOTES["RECEIVE_TRANSFER"].format(str(amount))
        )
        credit_transaction.generate_trx_id()

        wallet.add_balance(amount)
        try:
            session.add(credit_transaction)
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise TransactionError(error)
        #end try
        return credit_transaction
    #end def
#end class
