from functools import wraps
import traceback

from flask              import request, jsonify
from flask_restplus     import Resource
from flask_jwt_extended import jwt_refresh_token_required, jwt_required, get_jwt_identity, get_raw_jwt, verify_jwt_in_request, get_jwt_claims
from flask_jwt_extended.exceptions import RevokedTokenError

from app.api                        import jwt
from app.api.authentication         import api
from app.api.serializer             import UserSchema
from app.api.request_schema         import AuthRequestSchema
from app.api.errors                 import bad_request, internal_error, insufficient_scope
from app.api.models                 import BlacklistToken, User, Wallet, Role
from app.api.config                 import config

request_schema = AuthRequestSchema.parser

RESPONSE_MSG = config.Config.RESPONSE_MSG

"""
    CALLBACK JWT
"""

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
    return user.role.description
#end def

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({ "errors" : RESPONSE_MSG["FAILED"]["EXPIRED_TOKEN"] }), 401
#end def

@jwt.invalid_token_loader
def invalid_token_callback():
    return jsonify({ "errors" : RESPONSE_MSG["FAILED"]["INVALID_TOKEN"] }), 401
#end def

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({ "errors" : RESPONSE_MSG["FAILED"]["REVOKED_TOKEN"] }), 401
#end def

# CUSTOM DECORATOR
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except RevokedTokenError:
            return bad_request(RESPONSE_MSG["FAILED"]["REVOKED_TOKEN"])
        #end try

        current_role = get_jwt_claims()
        if current_role != "ADMIN":
            return insufficient_scope(RESPONSE_MSG["FAILED"]["INSUFFICIENT_PERMISSION"])
        else:
            return fn(*args, **kwargs)

    return wrapper
#end def

@api.errorhandler(RevokedTokenError)
def handle_revoked_token(error):
    print(error.message)

