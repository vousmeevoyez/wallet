from flask import render_template, url_for, request, jsonify

from app            import db
from app.access_key import bp
from app.models     import ApiKey
from app.serializer import ApiKeySchema
from app.errors     import bad_request, internal_error

from marshmallow    import ValidationError, pprint
from sqlalchemy.exc import IntegrityError

@bp.route('/create', methods=["GET", "POST"])
def create_wallet():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    try:
        params = request.form

        payload = {
                "type"              : 'createbilling',
                "client_id"         : request.args["client_id"],
                "trx_id"            : request.args["trx_id"],
                "trx_amount"        : request.args["trx_amount"],
                "billing_type"      : request.args["billing_type"],
                "customer_name"     : request.args["customer_name"],
                "customer_email"    : request.args["customer_email"],
                "customer_phone"    : request.args["customer_phone"],
                "virtual_account"   : request.args["virtual_account"],
                "datetime_expired"  : request.args["datetime_expired"]
        }

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

