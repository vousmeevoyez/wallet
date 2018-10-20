from flask import render_template, url_for, request, jsonify

from app            import db
from app.access_key import bp
from app.models     import ApiKey
from app.serializer import ApiKeySchema
from app.errors     import bad_request, internal_error

from marshmallow    import ValidationError, pprint
from sqlalchemy.exc import IntegrityError

@bp.route('/create', methods=["GET", "POST"])
def generate_access_key():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    try:
        params = request.form
        apikey = ApiKey( label=params["label"], name=params["name"])

        expiration = params["expiration"]
        db.session.add(apikey)
        try:
            apikey.generate_access_key(20,expiration)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return bad_request("Duplicate record")

    except Exception as e:
        return internal_error(str(e))

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

    access_key = request.args.get("token")
    access_key_status = ApiKey.check_access_key(access_key)

    if access_key_status is None:
        return bad_request("INVALID TOKEN")

    response["data"] = ApiKeySchema().dump(access_key_status).data

    return jsonify(response)
#end def

@bp.route('/revoke', methods=["GET"])
def revoke_access_key():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    access_key = request.args.get("token")
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

    access_key = request.args.get("token")
    result = ApiKey.query.filter_by(access_key=access_key).first()

    if result is None:
        return bad_request("Item not found")

    db.session.delete(result)
    db.session.commit()

    return jsonify(response)
#end def
