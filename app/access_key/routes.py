import traceback

from flask          import request, jsonify

from app.access_key         import bp
from app.serializer         import ApiKeySchema
from app.errors             import bad_request, internal_error
from app.access_key.modules import access_key


@bp.route('/create', methods=["POST"])
def create_access_key_routes():
    request_data = request.form

    data = {
        "username"   : request_data["username"],
        "password"   : request_data["password"],
        "label"      : request_data["label"],
        "name"       : request_data["name"],
        "expiration" : int(request_data["expiration"]),
    }

    # request data validator
    api_key, errors = ApiKeySchema().load(data)
    if errors:
        return jsonify(bad_request(errors))
    #end if

    response = access_key.AccessKeyController().create_access_key(api_key)

    return jsonify(response)
#end def

@bp.route('/list', methods=["GET"])
def list_access_key_routes():
    page = request.args.get("page")

    response = access_key.AccessKeyController().list_access_key(page)

    return jsonify(response)
#end def

@bp.route('/revoke', methods=["GET"])
def revoke_access_key_routes():
    access_key_id = request.args.get("id")

    response = access_key.AccessKeyController().revoke_access_key(access_key_id)

    return jsonify(response)
#end def

@bp.route('/check', methods=["GET"])
def check_access_key_routes():
    access_key_id = request.args.get("id")

    response = access_key.AccessKeyController().check_access_key(access_key_id)

    return jsonify(response)
#end def

@bp.route('/remove', methods=["GET"])
def remove_access_key_routes():
    access_key_id = request.args.get("id")

    response = access_key.AccessKeyController().remove_access_key(access_key_id)

    return jsonify(response)
#end def
