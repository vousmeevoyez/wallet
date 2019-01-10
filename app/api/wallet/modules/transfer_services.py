"""
    Transfer Services
    _________________
    this is module that serve request from wallet transfer :w
    routes
"""
from marshmallow    import ValidationError
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from flask          import request, jsonify

from app.api            import db
from app.api.models     import Wallet, Transaction, Payment, BankAccount
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config
from app.api.bank.handler import BankHandler

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
RESPONSE_MSG = config.Config.RESPONSE_MSG
WALLET_CONFIG = config.Config.WALLET_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
BNI_OPG_CONFIG = config.Config.BNI_OPG_CONFIG

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
        session.begin(subtransactions=True)

        source_account = params["source"]
        to = params["destination"]
        amount = params["amount"]
        payment_type = params["payment_type"]

        # build payment object
        payment = Payment(
            source_account=source_account,
            to=to,
            amount=amount,
            payment_type=payment_type,
        )
        session.add(payment)
        session.commit()

        return payment.id
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

        # CREATE TRANSACTION SESSION
        try:
            session = db.session(autocommit=True)
        except InvalidRequestError:
            db.session.commit()
            session = db.session()
        #end try
        session.begin(subtransactions=True)

        transfer_response = self._do_transaction(params, session)
        if transfer_response["status"] == "CLIENT_ERROR":
            return bad_request(transfer_response["data"])
        elif transfer_response["status"] == "SERVER_ERROR":
            return internal_error(transfer_response["data"])
        #end if

        session.commit()

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
        response = {
            "status" : "SUCCESS",
            "data"   : None
        }

        source      = params["source"     ]
        destination = params["destination"]
        amount      = params["amount"     ]
        pin         = params["pin"        ]

        if session is None:
            session = db.session
        #end if

        source_wallet = Wallet.query.filter_by(id=source).with_for_update().first()
        if source_wallet is None:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Wallet source not found"
            return response
        #end if

        if source_wallet.is_unlocked() is False:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Wallet source is locked"
            return response
        #end if

        if source_wallet.check_pin(pin) is not True:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Incorrect Pin"
            return response
        #end if

        if float(amount) > float(source_wallet.balance):
            response["status"] = "CLIENT_ERROR"
            response["data"] = RESPONSE_MSG["FAILED"]["INSUFFICIENT_BALANCE"]
            return response
        #end if

        destination_wallet = \
        Wallet.query.filter_by(id=destination).\
                with_for_update().first()
        if destination_wallet is None:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Wallet destination no found"
            return response
        #end if

        if destination_wallet.is_unlocked() is False:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Wallet destination is locked"
            return response
        #end if

        if destination_wallet == source_wallet:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Source & Destination wallet can't be same"
            return response
        #end if

        # lock account first
        lock_status = self._lock_account(source_wallet, destination_wallet, session)
        if lock_status is not True:
            response["status"] = "SERVER_ERROR"
            response["data"] = "Locking Failed"
            return response
        #end if

        # create debit payment
        params["payment_type"] = False # debit
        debit_payment_id = self._create_payment(params, session)

        # debit transaction
        debit_status = self._debit_transaction(source_wallet,\
                                               debit_payment_id,\
                                               amount, "IN", session)
        if debit_status is not True:
            response["status"] = "SERVER_ERROR"
            response["data"] = "Debit Transaction Failed"
            return response
        #end if

        # create credit payment
        params["payment_type"] = True # credit
        credit_payment_id = self._create_payment(params, session)

        # credit transaction
        credit_status = self._credit_transaction(destination_wallet,\
                                                 credit_payment_id,\
                                                 amount, session)
        if credit_status is not True:
            response["status"] = "SERVER_ERROR"
            response["data"  ] = "Credit Transaction Failed"
            return response
        #end if

        # unlock account
        unlock_status = self._unlock_account(source_wallet, destination_wallet, session)
        if unlock_status is not True:
            response["status"] = "SERVER_ERROR"
            response["data"] = "Unlocking Failed"
            return response
        #end if

        session.commit()
        return response
    #end def

    def _do_ext_transaction(self, params, session=None):
        response = {
            "status" : "SUCCESS",
            "data"   : None
        }

        source = params["source"]
        bank_account_id = params["destination"]
        amount = params["amount"]
        pin = params["pin"]

        if session is None:
            session = db.session
        #end if

        source_wallet = Wallet.query.filter_by(id=source).with_for_update().first()
        if source_wallet is None:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Wallet source not found"
            return response
        #end if

        if source_wallet.is_unlocked() is False:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Wallet source is locked"
            return response
        #end if

        if source_wallet.check_pin(pin) is not True:
            response["status"] = "CLIENT_ERROR"
            response["data"] = "Incorrect Pin"
            return response
        #end if

        if float(amount) > float(source_wallet.balance):
            response["status"] = "CLIENT_ERROR"
            response["data"] = RESPONSE_MSG["FAILED"]["INSUFFICIENT_BALANCE"]
            return response
        #end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(id=bank_account_id).first()

        # define source account
        source_account = BNI_OPG_CONFIG["MASTER_ACCOUNT"]

        # get information needed for transfer
        payment_payload = {
            "amount"         : amount,
            "source_account" : source_account,
            "account_no"     : bank_account.account_no,
            "bank_code"      : bank_account.bank.code,
        }
        payment_response = BankHandler("BNI").dispatch("TRANSFER",
                                                       payment_payload)
        if payment_response["status"] != "SUCCESS":
            response["status"] = "SERVER_ERROR"
            response["data"] = RESPONSE_MSG["FAILED"]["TRANSFER_FAILED"]
            return response
        #end if

        # lock account first
        source_wallet.lock()
        session.commit()

        # create debit payment
        params["payment_type"] = False # debit
        debit_payment_id = self._create_payment(params, session)

        # debit transaction
        debit_status = self._debit_transaction(source_wallet,\
                                               debit_payment_id,\
                                               amount, "OUT", session)
        if debit_status is not True:
            response["status"] = "SERVER_ERROR"
            response["data"] = "Debit Transaction Failed"
            return response
        #end if

        # unlock account
        source_wallet.unlock()

        session.commit()
        return response
    #end def

    def _lock_account(self, source, destination, session=None):
        """ function to lock account simultaneously"""
        if session is None:
            session = db.session
        #end if
        session.begin(subtransactions=True)
        try:
            source.lock()
            destination.lock()
            session.commit()
        except:
            session.rollback()
            return False
        #end try
        return True
    #end def

    def _unlock_account(self, source, destination, session=None):
        """ function to unlock account simultaneously"""
        if session is None:
            session = db.session
        #end if
        session.begin(subtransactions=True)
        try:
            source.unlock()
            destination.unlock()
            session.commit()
        except:
            session.rollback()
            return False
        #end try
        return True
    #end def

    def _debit_transaction(self, wallet, payment_id, amount, flag, session=None):
        if session is None:
            session = db.session
        #end if
        session.begin(subtransactions=True)

        amount = -float(amount)

        if flag == "IN":
            transaction_type = WALLET_CONFIG["IN_TRANSFER"]
        else:
            transaction_type = WALLET_CONFIG["OUT_TRANSFER"]
        #end if

        try:
            # debit (-) we increase balance
            debit_transaction = Transaction(
                payment_id=payment_id,
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=transaction_type,
                notes=TRANSACTION_NOTES["SEND_TRANSFER"].format(str(amount))
            )
            debit_transaction.generate_trx_id()

            wallet.add_balance(amount)
            session.add(debit_transaction)

            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
            return False
        #end try
        return True
    #end def

    def _credit_transaction(self, wallet, payment_id, amount, session=None):
        if session is None:
            session = db.session
        #end if
        session.begin(subtransactions=True)

        amount = float(amount)

        try:
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
            session.add(credit_transaction)

            session.commit()
        except:
            session.rollback()
            return False
        #end try
        return True
    #end def
#end class
