import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError

from app            import db
from app.wallet     import bp
from app.bank       import handler as bank_handler
from app.models     import Wallet, Transaction, VirtualAccount
from app.serializer import WalletSchema, TransactionSchema, VirtualAccountSchema
from app.errors     import bad_request, internal_error, request_not_found
from app.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
WALLET_CONFIG     = config.Config.WALLET_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
RESPONSE_MSG      = config.Config.RESPONSE_MSG

@bp.route('/create', methods=["POST"])
def generate_wallet():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        # parse request data 
        request_data = request.form
        name       = request_data["name"  ]
        msisdn     = request_data["msisdn"]
        email      = request_data["email" ]
        pin        = request_data["pin"   ]

        data = {
            "name"       : name,
            "msisdn"     : msisdn,
            "email"      : email,
            "pin"        : pin,
        }

        # request data validator
        wallet, errors = WalletSchema().load(data)
        if errors:
            return bad_request(errors)
        #end if

        try:
            wallet_id = wallet.generate_wallet_id()
            wallet.set_pin(pin)
            db.session.add(wallet)

            # GENERATE VIRTUAL ACCOUNT INFORMATION 
            va = VirtualAccount(
                name=name,
                wallet_id=wallet.id,
                status=True# inactive
            )
            va_id  = va.generate_va_number()
            trx_id = va.generate_trx_id()

            db.session.add(va)
            db.session.commit()

            # GENERATE REAL VIRTUAL ACCOUNT ON BANK

            # modify msisdn so match BNI format
            customer_phone = msisdn[1:]
            fixed = "62"
            customer_phone = fixed + customer_phone

            # generate expires time
            datetime_expired = datetime.now() + timedelta(hours=WALLET_CONFIG["VA_TIMEOUT"])
            expires_in       = datetime_expired.timestamp()

            va_payload = {
                "trx_id"           : str(trx_id),
                "amount"           : "0",
                "customer_name"    : name,
                "customer_phone"   : customer_phone,
                "virtual_account"  : str(va_id),
                "datetime_expired" : datetime_expired.strftime("%Y-%m-%d %H:%M:%S"),
            }

            # request create VA
            result = bank_handler.EcollectionHandler().create_va("CREDIT", va_payload)

            if result["status"] != "SUCCESS":
                return bad_request(RESPONSE_MSG["VA_CREATION_FAILED"])

        except IntegrityError as err:
            db.session.rollback()
            return bad_request(RESPONSE_MSG["ERROR_ADDING_RECORD"])
        #end try

        response["data"          ] = { "wallet_id" : wallet_id }
        response["status_message"] = RESPONSE_MSG["WALLET_CREATED"]

    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
        return internal_error()
    #end try

    return jsonify(response)
#end def

@bp.route('/list', methods=["GET"])
def wallet_list():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        wallet = Wallet.query.all()
        response["data"] = WalletSchema(many=True).dump(wallet).data
    except Exception as e:
        print(str(e))
        return internal_error()
    #end try

    return jsonify(response)
#end def

@bp.route('/get_info', methods=["POST"])
def get_wallet_details():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        # parse request data 
        request_data = request.form
        wallet_id  = request_data["id" ]
        pin        = request_data["pin"]

        data = {
            "wallet_id": wallet_id,
            "pin"      : pin,
        }

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found()

        if wallet.check_pin(pin) != True:
            return bad_request(RESPONSE_MSG["INCORRECT_PIN"])
        #end if

        wallet_information = WalletSchema().dump(wallet).data
        va_information     = VirtualAccountSchema().dump(wallet.virtual_account).data

        response["data"] = {
            "wallet" : wallet_information,
            "virtual_account" : va_information
        }

    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def


@bp.route('/remove', methods=["GET"])
def remove_wallet():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        # parse request data 
        wallet_id = request.args.get("id")

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found()

        db.session.delete(wallet)
        db.session.commit()
        response["data"] = RESPONSE_MSG["WALLET_REMOVED"]

    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def

@bp.route('/check_balance', methods=["POST"])
def check_wallet_balance():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        # parse request data 
        request_data = request.form
        wallet_id  = request_data["id"]
        pin        = request_data["pin"   ]

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found()

        if wallet.check_pin(pin) != True:
            return bad_request(RESPONSE_MSG["INCORRECT_PIN"])

        response["data"] = {
            "id" : wallet_id,
            "balance" : wallet.balance
        }

    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def

@bp.route('/lock', methods=["GET"])
def lock_wallet():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        # parse request data 
        wallet_id = request.args.get("id")

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found()

        if wallet.is_unlocked() != True:
            return bad_request( RESPONSE_MSG["WALLET_ALREADY_LOCKED"])

        wallet.lock()
        db.session.commit()

        response["data"] = RESPONSE_MSG["WALLET_LOCKED"]
    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def


@bp.route('/unlock', methods=["GET"])
def unlock_wallet():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        # parse request data 
        wallet_id = request.args.get("id")

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found()

        if wallet.is_unlocked() != False:
            return bad_request(RESPONSE_MSG["WALLET_ALREADY_UNLOCKED"])

        wallet.unlock()
        db.session.commit()

        response["data"] = RESPONSE_MSG["WALLET_UNLOCKED"]
    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def

@bp.route('/deposit', methods=["POST"])
def deposit():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        # parse request data 
        request_data = request.form
        wallet_id  = request_data["wallet_id"]
        amount     = float(request_data["amount"])

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found()

        if wallet.is_unlocked() == False:
            return bad_request(RESPONSE_MSG["TRANSACTION_LOCKED"])

        """
        master_wallet_id = WALLET_CONFIG["MASTER_WALLET_ID"]
        master_wallet = Wallet.query.filter_by(id=master_wallet_id).first()

        # check balance
        if master_wallet.balance < amount:
            return bad_request(RESPONSE_MSG["INSUFFICIENT_BALANCE"])
        """

        try:
            """
            # start transaction here
            # debit_transaction (-) we deduct balance first
            debit_transaction = Transaction(
                source_id=master_wallet.id,
                destination_id=wallet.id,
                amount=amount,
                transaction_type=WALLET_CONFIG["DEBIT_FLAG"],
                notes=TRANSACTION_NOTES["INJECT"].format(str(amount))
            )
            debit_transaction.generate_trx_id()
            master_wallet.deduct_balance(amount)
            db.session.add(debit_transaction)
            """

            # credit (+) we increase balance 
            credit_transaction = Transaction(
                source_id=wallet.id,
                destination_id=wallet.id,
                amount=amount,
                transaction_type=WALLET_CONFIG["CREDIT_FLAG"],
                transfer_type=WALLET_CONFIG["BANK_TO_VA"],
                notes=TRANSACTION_NOTES["DEPOSIT"].format(str(amount))
            )
            credit_transaction.generate_trx_id()
            wallet.add_balance(amount)
            db.session.add(credit_transaction)

            db.session.commit()
        except:
            db.session.rollback()
            print(traceback.format_exc())
            return internal_error()

        success_message = RESPONSE_MSG["SUCCESS_DEPOSIT"].format(str(amount), wallet_id)
        response["data"] = success_message
    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def

@bp.route('/transaction_history', methods=["GET"])
def wallet_mutation():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    try:
        # parse request data 
        wallet_id = request.args.get("id")

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found()

        wallet_response = Transaction.query.filter_by(source_id=wallet_id ,destination_id=wallet_id)

        response["data"] = TransactionSchema(many=True).dump(wallet_response).data

    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def
