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

        transfer_response = self._do_transaction(source, destination, amount, pin, transfer_type)
        if transfer_response["status"] != "SUCCESS":
            response["status_message"] = transfer_response["status"]
            response["data"          ] = transfer_response["data"]
            return response
        #end if

        response["data"] = RESPONSE_MSG["SUCCESS_TRANSFER"].format( str(amount), str(source), str(destination) )

        return response
    #end def

    def _do_transaction(self, source, destination, amount, pin, transfer_type):
        response = { "status" : "SUCCESS", "data" : ""}

        source_wallet = Wallet.query.filter_by(id=source).first()
        print(source_wallet)
        if source_wallet == None:
            response["status"] = "FAILED"
            response["data"  ] = "Wallet source not found"
            return response

        if source_wallet.is_unlocked() == False:
            response["status"] = "FAILED"
            response["data"  ] = "Wallet source is locked"
            return response

        if source_wallet.check_pin(pin) != True:
            response["status"] = "FAILED"
            response["data"  ] = "Incorrect pin"
            return response

        destination_wallet = Wallet.query.filter_by(id=destination).first()
        print(destination_wallet)
        if destination_wallet == None:
            response["status"] = "FAILED"
            response["data"  ] = "Wallet destination not found"
            return response

        if destination_wallet.is_unlocked() == False:
            response["status"] = "FAILED"
            response["data"  ] = "Wallet destination is locked"
            return response

        try:
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
        except:
            print(traceback.format_exc())
            response["status"] = "FAILED"
            db.session.rollback()

        return response
    #end def

#end class
