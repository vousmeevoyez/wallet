from flask import render_template, url_for, request, jsonify

from app            import db
from app.auth       import bp
from app.models     import UserWallet
from app.serializer import UserWalletScheme
from app.errors     import bad_request, internal_error

from marshmallow    import ValidationError, pprint
from sqlalchemy.exc import IntegrityError

@bp.route('/create', methods=["GET", "POST"])
def generate_wallet():
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

    except ValidationError as err:
        return jsonify(err.messages)

    return jsonify(response)
#end def

@bp.route('/list', methods=["GET"])
def list_access_token():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    try:
        query_result = ApiKey.query.all()
        result = ApiKeySchema(many=True).dump(query_result)
        response["data"] = result.data
    except ValidationError as err:
        return jsonify(err.messages)

    return jsonify(response)
#end def
