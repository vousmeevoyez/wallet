from flask          import request, jsonify

from app            import db
from app.access_key import bp
from app.models     import ApiKey
from app.serializer import ApiKeySchema
from app.errors     import bad_request, internal_error
from app.config     import config

from marshmallow    import ValidationError, pprint
from sqlalchemy.exc import IntegrityError

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG

@bp.route('/create', methods=["POST"])
def generate_access_key():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    try:

        try:
            # parse request data 
            request_data = request.form
            label      = request_data["label"      ]
            name       = request_data["name"       ]
            expiration = request_data["expiration" ]

            data = {
                "label"      : label,
                "name"       : name,
                "expiration" : int(expiration),
            }

            # request data validator
            result,errors = ApiKeySchema().load(data)
            if errors:
                return bad_request(errors)

            try:
                result.generate_access_key(ACCESS_KEY_CONFIG["TOKEN_LENGTH"])
                result.set_expiration(ACCESS_KEY_CONFIG["EXPIRE_IN"])
                db.session.add(result)
                result.generate_access_key(ACCESS_KEY_CONFIG["TOKEN_LENGTH"])
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return bad_request("Error adding record")

            response["data"] = "Secret key successfully created"
        except ValidationError as err:
            return bad_request(err.messages)

    except Exception as e:
        print(str(e))
        return internal_error()

    return jsonify(response)
#end def

@bp.route('/list', methods=["GET"])
def list_access_key():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    try:
        query_result = ApiKey.query.all()
        result = ApiKeySchema(many=True).dump(query_result)
        response["data"] = result.data
    except ValidationError as err:
        return jsonify(err.messages)

    return jsonify(response)
#end def

@bp.route('/check', methods=["GET"])
def check_access_key():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    access_key = request.args.get("id")
    access_key_status = ApiKey.check_access_key(access_key)

    if access_key_status is None:
        return bad_request("INVALID TOKEN")

    response["data"] = ApiKeySchema().dump(access_key_status).data

    return jsonify(response)
#end def

@bp.route('/revoke', methods=["GET"])
def revoke_access_key():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    access_key = request.args.get("id")
    result = ApiKey.query.filter_by(access_key=access_key).first()

    if result is None:
        return bad_request("Item not found")

    result.revoke_access_key()
    db.session.commit()

    return jsonify(response)
#end def

@bp.route('/remove', methods=["GET"])
def remove_access_key():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    access_key = request.args.get("id")
    result = ApiKey.query.filter_by(access_key=access_key).first()

    if result is None:
        return bad_request("Item not found")

    db.session.delete(result)
    db.session.commit()

    return jsonify(response)
#end def
