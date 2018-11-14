import traceback

from marshmallow    import ValidationError
from sqlalchemy.exc import IntegrityError
from flask          import request, jsonify

from app            import db
from app.transfer   import bp
from app.models     import Wallet, Transaction
from app.serializer import TransactionSchema
from app.errors     import bad_request, internal_error, request_not_found
from app.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
RESPONSE_MSG      = config.Config.RESPONSE_MSG
WALLET_CONFIG     = config.Config.WALLET_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES

class TransferController:

    def __init__(self):
        pass
    #end def

    def internal_transfer(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        source      = params["source"     ]
        destination = params["destination"]
        amount      = params["amount"     ]
        pin         = params["pin"        ]
        transfer_type = "VA_TO_VA"

        transfer_response = self._do_transaction_v2(source, destination, amount, pin, transfer_type)
        if transfer_response["status"] != "SUCCESS":
            if transfer_response["code"] == 404:
                return request_not_found(transfer_response["data"])
            elif transfer_response["code"] == 400:
                return bad_request(transfer_response["data"])
            #end if
        #end if

        response["data"] = RESPONSE_MSG["SUCCESS_TRANSFER"].format( str(amount), str(source), str(destination) )

        return response
    #end def

    def _do_transaction_v2(self, source, destination, amount, pin, transfer_type):
        response = {
            "code"   : 0,
            "status" : "SUCCESS",
            "data"   : ""
        }

        source_wallet = Wallet.query.filter_by(id=source).first()
        if source_wallet == None:
            response["status"] = "FAILED"
            response["code"  ] = 404
            response["data"  ] = "Wallet source not found"
            return response
        #end if

        if source_wallet.is_unlocked() == False:
            response["status"] = "FAILED"
            response["code"  ] = 400
            response["data"  ] = "Wallet source is locked"
            return response
        #end if

        if source_wallet.check_pin(pin) != True:
            response["status"] = "FAILED"
            response["code"  ] = 400
            response["data"  ] = "Incorrect pin"
            return response
        #end if

        if float(amount) > float(source_wallet.balance):
            response["status"] = "FAILED"
            response["code"  ] = 400
            response["data"  ] = "Insufficient Balance for this transaction"
            return response
        #end if

        destination_wallet = Wallet.query.filter_by(id=destination).first()
        if destination_wallet == None:
            response["status"] = "FAILED"
            response["code"  ] = 404
            response["data"  ] = "Wallet destination not found"
            return response
        #end if

        if destination_wallet.is_unlocked() == False:
            response["status"] = "FAILED"
            response["code"  ] = 400
            response["data"  ] = "Wallet destination is locked"
            return response
        #end if

        try:
            source_wallet.lock()
            destination_wallet.lock()
            db.session.commit()

            # debit(-) we deduct balance first
            debit_transaction = Transaction(
                source_id=source_wallet.id,
                destination_id=destination_wallet.id,
                amount=amount,
                transaction_type=WALLET_CONFIG["DEBIT_FLAG"],
                transfer_type=WALLET_CONFIG[transfer_type],
                notes=TRANSACTION_NOTES["SEND_TRANSFER"].format(str(amount))
            )
            debit_transaction.generate_trx_id()
            source_wallet.deduct_balance(amount)
            db.session.add(debit_transaction)

            # credit (+) we increase balance 
            credit_transaction = Transaction(
                source_id=destination_wallet.id,
                destination_id=source_wallet.id,
                amount=amount,
                transaction_type=WALLET_CONFIG["CREDIT_FLAG"],
                transfer_type=WALLET_CONFIG[transfer_type],
                notes=TRANSACTION_NOTES["RECEIVE_TRANSFER"].format(str(amount))
            )
            credit_transaction.generate_trx_id()
            destination_wallet.add_balance(amount)
            db.session.add(credit_transaction)

            db.session.commit()

            source_wallet.unlock()
            destination_wallet.unlock()
            db.session.commit()
        except:
            db.session.rollback()
            print(traceback.format_exc())
            response["status"] = "FAILED"

        return response
    #end def

    def _do_transaction(self, source, destination, amount, pin, transfer_type):
        response = {
            "code"   : 0,
            "status" : "SUCCESS",
            "data"   : ""
        }

        source_wallet = Wallet.query.filter_by(id=source).first()
        if source_wallet == None:
            response["status"] = "FAILED"
            response["code"  ] = 404
            response["data"  ] = "Wallet source not found"
            return response
        #end if

        if source_wallet.is_unlocked() == False:
            response["status"] = "FAILED"
            response["code"  ] = 400
            response["data"  ] = "Wallet source is locked"
            return response
        #end if

        if source_wallet.check_pin(pin) != True:
            response["status"] = "FAILED"
            response["code"  ] = 400
            response["data"  ] = "Incorrect pin"
            return response
        #end if

        if float(amount) > float(source_wallet.balance):
            response["status"] = "FAILED"
            response["code"  ] = 400
            response["data"  ] = "Insufficient Balance for this transaction"
            return response
        #end if

        destination_wallet = Wallet.query.filter_by(id=destination).first()
        if destination_wallet == None:
            response["status"] = "FAILED"
            response["code"  ] = 404
            response["data"  ] = "Wallet destination not found"
            return response
        #end if

        if destination_wallet.is_unlocked() == False:
            response["status"] = "FAILED"
            response["code"  ] = 400
            response["data"  ] = "Wallet destination is locked"
            return response
        #end if

        session = db.session(autocommit=True)
        session.begin(subtransactions=True)

        try:
            # lock account first 
            self._lock_account(session, source_wallet, destination_wallet)

            # debit transaction
            self._debit_transaction(session, source_wallet, destination_wallet, amount, transfer_type)

            # credit transaction
            self._credit_transaction(session, source_wallet, destination_wallet, amount, transfer_type)

            # unlock account
            self._unlock_account(session, source_wallet, destination_wallet)

            session.commit()
        except:
            session.rollback()
            print(traceback.format_exc())
            response["status"] = "FAILED"

        return response
    #end def

    def _lock_account(self, session, source, destination):
        session.begin(subtransactions=True)
        try:
            source.lock()
            destination.lock()
            session.commit()
        except:
            session.rollback()
        #end try
    #end def

    def _unlock_account(self, session, source, destination):
        session.begin(subtransactions=True)
        try:
            source.unlock()
            destination.unlock()
            session.commit()
        except:
            session.rollback()
        #end try
    #end def

    def _add_balance(self, session, wallet, amount):
        session.begin(subtransactions=True)
        try:
            wallet.add_balance(amount)
            session.commit()
        except:
            session.rollback()
        #end try
    #end def

    def _reduce_balance(self, session, wallet, amount):
        session.begin(subtransactions=True)
        try:
            wallet.deduct_balance(amount)
            session.commit()
        except:
            session.rollback()
        #end try
    #end def

    def _debit_transaction(self, session, source, destination, amount, transfer_type):
        session.begin(subtransactions=True)
        try:
            # debit(-) we deduct balance first
            debit_transaction = Transaction(
                source_id=source.id,
                destination_id=destination.id,
                amount=amount,
                transaction_type=WALLET_CONFIG["DEBIT_FLAG"],
                transfer_type=WALLET_CONFIG[transfer_type],
                notes=TRANSACTION_NOTES["SEND_TRANSFER"].format(str(amount))
            )
            debit_transaction.generate_trx_id()
            session.add(debit_transaction)

            self._reduce_balance(session, source)

            session.commit()
        except:
            session.rollback()
        #end try
    #end def

    def _credit_transaction(self, session, source, destination, amount, transfer_type):
        session.begin(subtransactions=True)
        try:
            # credit (+) we increase balance 
            credit_transaction = Transaction(
                source_id=destination.id,
                destination_id=source.id,
                amount=amount,
                transaction_type=WALLET_CONFIG["CREDIT_FLAG"],
                transfer_type=WALLET_CONFIG[transfer_type],
                notes=TRANSACTION_NOTES["RECEIVE_TRANSFER"].format(str(amount))
            )
            credit_transaction.generate_trx_id()
            session.add(credit_transaction)

            self._add_balance(session, destination)

            session.commit()
        except:
            session.rollback()
        #end try
    #end def

#end class
