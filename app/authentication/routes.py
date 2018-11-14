from functools import wraps
import traceback

from flask              import request, jsonify
from flask_jwt_extended import jwt_refresh_token_required, jwt_required, get_jwt_identity, get_raw_jwt, verify_jwt_in_request, get_jwt_claims

from app                        import jwt
from app.authentication         import bp
from app.serializer             import UserSchema
from app.errors                 import bad_request, internal_error
from app.authentication.modules import authentication
from app.models                 import BlacklistToken, User, Wallet

@jwt.token_in_blacklist_loader
def check_token_blacklist(decrypted_token):
    token = decrypted_token["jti"]
    return BlacklistToken.is_blacklisted(token)
#end def

@jwt.user_identity_loader
def add_identity(user):
    return user.id
#end def

@jwt.user_claims_loader
def add_claim(user):
    return user.role
#end def

# CUSTOM DECORATOR
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        role = get_jwt_claims()
        if role != 1:
            return jsonify(msg='Insufficient Permission'), 403
        else:
            return fn(*args, **kwargs)
    return wrapper
#end def

@bp.route('/request_token', methods=["POST"])
def create_access_token():
    request_data = request.form
    data = {
        "username"   : request_data["username"],
        "password"   : request_data["password"],
    }

    # request data validator
    errors = UserSchema().validate(data, partial=("name","msisdn","email"))
    if errors:
        return jsonify(bad_request(errors))
    #end if

    response = authentication.AuthController().create_token(data)

    return jsonify(response)
#end def

@bp.route('/refresh', methods=["GET"])
@jwt_refresh_token_required
def create_refresh_token():
    current_user = get_jwt_identity()
    response = authentication.AuthController().refresh_token(current_user)

    return jsonify(response)
#end def

@bp.route('/logout_access', methods=["POST"])
@jwt_required
def logout_access_token_routes():
    token = get_raw_jwt()["jti"]
    response = authentication.AuthController().logout_access_token(token)

    return jsonify(response)
#end def

@bp.route('/logout_refresh', methods=["POST"])
@jwt_refresh_token_required
def logout_refresh_token_routes():
    token = get_raw_jwt()["jti"]
    response = authentication.AuthController().logout_refresh_token(token)

    return jsonify(response)
#end def
