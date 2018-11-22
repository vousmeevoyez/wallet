import traceback

from flask import request, jsonify
from flask_jwt_extended import jwt_refresh_token_required, jwt_required, get_jwt_identity, get_jwt_claims, get_raw_jwt

from app.transfer           import bp
from app.serializer         import TransactionSchema
from app.transfer.modules   import transfer
from app.authentication     import helper as auth_helper

@bp.route('/direct', methods=["POST"])
@jwt_required
def virtual_transfer():
    user_id = get_jwt_identity()

    # parse request data 
    request_data = request.form
    data = {
        "source"      : request_data["source"],
        "destination" : request_data["destination"],
        "amount"      : request_data["amount"],
        "notes"       : request_data["notes"],
        "pin"         : request_data["pin"],
    }

    # checking token identity to make sure user can only access their wallet information
    permission_response = auth_helper.AuthenticationHelper().check_wallet_permission(user_id, data["source"])
    if permission_response != None:
        return jsonify(permission_response)
    #end if

    # request data validator
    errors = TransactionSchema().validate(data)
    if errors:
        return jsonify(bad_request(errors))
    #end if


    response = transfer.TransferController().internal_transfer(data)

    return jsonify(response)
#end def
