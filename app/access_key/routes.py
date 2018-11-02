import traceback

from flask          import request, jsonify
from marshmallow    import ValidationError, pprint
from sqlalchemy.exc import IntegrityError

from app            import db
from app.access_key import bp
from app.models     import ApiKey
from app.serializer import ApiKeySchema
from app.errors     import bad_request, internal_error
from app.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG


@bp.route('/create', methods=["POST"])
def generate_access_key():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data"           : "NONE"
    }

    try:
        # parse request data 
        request_data = request.form
        username   = request_data["username"   ]
        password   = request_data["password"   ]
        label      = request_data["label"      ]
        name       = request_data["name"       ]
        expiration = request_data["expiration" ]

        data = {
            "username"   : username,
            "password"   : password,
            "label"      : label,
            "name"       : name,
            "expiration" : int(expiration),
        }

        # request data validator
        api_key, errors = ApiKeySchema().load(data)
        if errors:
            return bad_request(errors)
        #end if

        try:
            api_key.generate_access_key(ACCESS_KEY_CONFIG["TOKEN_LENGTH"])
            api_key.set_expiration(ACCESS_KEY_CONFIG["EXPIRE_IN"])
            api_key.set_expiration(ACCESS_KEY_CONFIG["EXPIRE_IN"])

            db.session.add(api_key)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return bad_request("Error adding record")
        #end try

        response["data"] = "Secret key successfully created"

    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
        return internal_error()
    #end try

    return jsonify(response)
#end def


@bp.route('/list', methods=["GET"])
def list_access_key():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data"           : "NONE"
    }

    query_result = ApiKey.query.all()
    result,errors = ApiKeySchema(many=True).dump(query_result)
    if errors:
        return bad_request(errors)
    #end if

    response["data"] = result

    return jsonify(response)
#end def


@bp.route('/check', methods=["GET"])
def check_access_key():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data"           : "NONE"
    }

    access_key = request.args.get("id")
    access_key_status = ApiKey.check_access_key(access_key)

    if access_key_status is None:
        return bad_request("INVALID TOKEN")
    #end if

    result.errors = ApiKeySchema().dump(access_key_status).data
    if errors:
        return bad_request(errors)
    #end if

    response["data"] = result

    return jsonify(response)
#end def


@bp.route('/revoke', methods=["GET"])
def revoke_access_key():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data"           : "NONE"
    }

    access_key = request.args.get("id")
    result = ApiKey.query.filter_by(access_key=access_key).first()

    if result is None:
        return bad_request("Item not found")
    #end if

    result.revoke_access_key()
    db.session.commit()

    return jsonify(response)
#end def


@bp.route('/remove', methods=["GET"])
def remove_access_key():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data"           : "NONE"
    }

    access_key = request.args.get("id")
    result = ApiKey.query.filter_by(access_key=access_key).first()

    if result is None:
        return bad_request("Item not found")
    #end if

    db.session.delete(result)
    db.session.commit()

    return jsonify(response)
#end def
