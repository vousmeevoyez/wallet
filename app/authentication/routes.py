import traceback

from flask          import request, jsonify

from app                        import jwt
from app.authentication         import bp
from app.serializer             import UserSchema
from app.errors                 import bad_request, internal_error
from app.authentication.modules import authentication

@bp.route('/request', methods=["POST"])
def create_token():
    request_data = request.form
    data = {
        "username"   : request_data["username"],
        "password"   : request_data["password"],
    }

    # request data validator
    errors = UserSchema().validate(data)
    if errors:
        return jsonify(bad_request(errors))
    #end if

    response = authentication.AuthController().create_token(data)

    return jsonify(response)
#end def

