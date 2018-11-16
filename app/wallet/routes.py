import traceback
from flask              import request, jsonify
from flask_jwt_extended import jwt_refresh_token_required, jwt_required, get_jwt_identity, get_jwt_claims, get_raw_jwt

from app.wallet                 import bp
from app.serializer             import WalletSchema
from app.errors                 import bad_request, internal_error, request_not_found
from app.config                 import config
from app.wallet.modules         import wallet
from app.authentication         import routes as custom_decorator
from app.authentication         import helper as auth_helper

RESPONSE_MSG = config.Config.RESPONSE_MSG

@bp.route('/create', methods=["POST"])
@jwt_required
def create_wallet():
    user_id = get_jwt_identity()

    request_data = request.form
    data = {
        "name"   : request_data["name"   ],
        "msisdn" : request_data["msisdn" ],
        "pin"    : request_data["pin"    ],
        "user_id": request_data["user_id"]
    }

    # to prevent token to access another user information
    if str(user_id) != data["user_id"]:
        return jsonify(bad_request(RESPONSE_MSG["UNAUTHORIZED_USER"]))
    #end if

    response = wallet.WalletController().create(data)
    return jsonify(response)
#end def

@bp.route('/list', methods=["GET"])
@jwt_required
def wallet_list():
    user_id = get_jwt_identity()

    data = {
        "user_id" : request.args.get("id")
    }

    # to prevent token to access another user information
    if str(user_id) != data["user_id"]:
        return jsonify(bad_request(RESPONSE_MSG["UNAUTHORIZED_USER"]))
    #end if

    response = wallet.WalletController().list(data)
    return jsonify(response)
#end def

@bp.route('/deposit', methods=["POST"])
@custom_decorator.admin_required
def deposit():
    request_data = request.form
    data = {
        "id"     : request_data["wallet_id"],
        "amount" : request_data["amount"   ],
    }

    response = wallet.WalletController().deposit(data)
    return jsonify(response)
#end def

@bp.route('/info', methods=["POST", "DELETE"])
@jwt_required
def wallet_info():
    user_id = get_jwt_identity()

    request_data = request.form
    data = {
        "id"  : request_data["wallet_id"],
        "pin" : request_data["pin"      ],
    }

    # checking token identity to make sure user can only access their wallet information
    permission_response = auth_helper.AuthenticationHelper().check_wallet_permission(user_id, data["id"])
    if permission_response != None:
        return jsonify(permission_response)
    #end if

    if request.method == "POST":
        response = wallet.WalletController().details(data)
    elif request.method == "DELETE":
        response = wallet.WalletController().remove(data)
    #end if

    return jsonify(response)
#end def

@bp.route('/transaction_history', methods=["GET"])
@jwt_required
def wallet_mutation():
    user_id = get_jwt_identity()

    wallet_id = request.args.get("id")
    # checking token identity to make sure user can only access their wallet information
    permission_response = auth_helper.AuthenticationHelper().check_wallet_permission(user_id, wallet_id)
    if permission_response != None:
        return jsonify(permission_response)
    #end if

    response = wallet.WalletController().history(wallet_id)
    return jsonify(response)
#end def

@bp.route('/balance', methods=["POST"])
@jwt_required
def check_wallet_balance_routes():
    user_id = get_jwt_identity()

    request_data = request.form
    data = {
        "id"  : request_data["wallet_id"],
        "pin" : request_data["pin"      ],
    }

    # checking token identity to make sure user can only access their wallet information
    permission_response = auth_helper.AuthenticationHelper().check_wallet_permission(user_id, data["id"])
    if permission_response != None:
        return jsonify(permission_response)
    #end if

    response = wallet.WalletController().check_balance(data)
    return jsonify(response)
#end def
