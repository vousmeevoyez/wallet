from flask          import request, jsonify

from app            import db
from app.transfer   import bp
from app.models     import Wallet, Transaction
from app.serializer import TransactionSchema
from app.errors     import bad_request, internal_error, request_not_found
from app.config     import config

from marshmallow    import ValidationError
from sqlalchemy.exc import IntegrityError

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
RESPONSE_MSG      = config.Config.RESPONSE_MSG

@bp.route('/direct', methods=["POST"])
def virtual_transfer():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    try:
        # parse request data 
        request_data = request.form
        source      = request_data["source"     ]
        destination = request_data["destination"]
        amount      = request_data["amount"     ]
        notes       = request_data["notes"      ]
        pin         = request_data["pin"        ]

        data = {
            "source"      : source,
            "destination" : destination,
            "amount"      : amount,
            "notes"       : notes,
            "pin"         : pin,
        }

        # request data validator
        transaction, errors = TransactionSchema().load(data)
        if errors:
            return bad_request(errors)

        result = _do_transaction(source, destination, amount, "VA_TO_VA")
        if result["status"] != "SUCCESS":
            return bad_request(result["data"])

        response["data"] = RESPONSE_MSG["SUCCESS_TRANSFER"].format(str(destination), str(amount))

    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def

def _do_transaction(source, destination, amount, pin, transfer_type):
    response = { "status" : "SUCCESS", "data" : ""}

    source_wallet = Wallet.query.filter_by(id=source).first()
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
            source_id=master_wallet.id,
            destination_id=wallet.id,
            amount=amount,
            transaction_type=WALLET_CONFIG["DEBIT_FLAG"],
            transfer_type=WALLET_CONFIG[transfer_type],
            notes=TRANSACTION_NOTES["INJECT"].format(str(amount))
        )
        debit_transaction.generate_trx_id()
        master_wallet.deduct_balance(amount)
        db.session.add(debit_transaction)

        # credit (+) we increase balance 
        credit_transaction = Transaction(
            source_id=wallet.id,
            destination_id=master_wallet.id,
            amount=amount,
            transaction_type=WALLET_CONFIG["CREDIT_FLAG"],
            transfer_type=WALLET_CONFIG[transfer_type],
            notes=TRANSACTION_NOTES["DEPOSIT"].format(str(amount))
        )
        credit_transaction.generate_trx_id()
        wallet.add_balance(amount)
        db.session.add(credit_transaction)

        db.session.commit()
    except:
        response["status"] = "FAILED"
        db.session.rollback()

    return response
#end def
