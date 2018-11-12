import traceback
from flask          import request, jsonify

from app.wallet             import bp
from app.serializer         import WalletSchema
from app.errors             import bad_request, internal_error, request_not_found
from app.config             import config
from app.wallet.modules     import wallet

@bp.route('/create', methods=["POST"])
def create_wallet():
    request_data = request.form
    data = {
        "name"   : request_data["name"   ],
        "msisdn" : request_data["msisdn" ],
        "pin"    : request_data["pin"    ],
        "user_id": request_data["user_id"]
    }

    response = wallet.WalletController().create(data)
    return jsonify(response)
#end def

@bp.route('/list', methods=["GET"])
def wallet_list():
    data = {
        "user_id" : request.args.get("id")
    }

    response = wallet.WalletController().list(data)
    return jsonify(response)
#end def

@bp.route('/deposit', methods=["POST"])
def deposit():
    request_data = request.form
    data = {
        "wallet_id" : request_data["wallet_id"],
        "amount"    : request_data["amount"   ],
    }

    response = wallet.WalletController().deposit(data)
    return jsonify(response)
#end def

@bp.route('/info', methods=["POST", "DELETE"])
def wallet_info():
    request_data = request.form
    data = {
        "id"  : request_data["wallet_id"],
        "pin" : request_data["pin"      ],
    }

    if request.method == "POST":
        response = wallet.WalletController().details(data)
    elif request.method == "DELETE":
        response = wallet.WalletController().remove(data)

    return jsonify(response)
#end def

@bp.route('/transaction_history', methods=["GET"])
def wallet_mutation():
    wallet_id = request.args.get("id")

    response = wallet.WalletController().history(wallet_id)
    return jsonify(response)
#end def

@bp.route('/balance', methods=["POST"])
def check_wallet_balance_routes():
    request_data = request.form
    data = {
        "id"  : request_data["wallet_id"],
        "pin" : request_data["pin"      ],
    }

    response = wallet.WalletController().check_balance(data)
    return jsonify(response)
#end def
