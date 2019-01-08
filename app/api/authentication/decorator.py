""" 
    Auth Decorator
    ________________
    this is module that contain various decorator to protect various endpoint
"""
from functools import wraps

from flask_restplus     import reqparse

from app.api.authentication.modules.auth_services import AuthServices
from app.api.request_schema         import AuthRequestSchema
from app.api.errors                 import bad_request, internal_error, insufficient_scope, method_not_allowed
from app.api.config                 import config

request_schema = AuthRequestSchema.parser

RESPONSE_MSG = config.Config.RESPONSE_MSG

# CUSTOM DECORATOR
def admin_required(fn):
    """
        decorator to only allow admin access this function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # define header schema
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers', required=True)
        header = parser.parse_args()

        # accessing token from header
        auth_header = header["Authorization"]
        token = auth_header.split(" ")[1]

        response = AuthServices.current_login_user(token)

        if response["status"] != "SUCCESS":
            return bad_request(response["data"])
        #end if

        if response["data"]["role"] != "ADMIN":
            return insufficient_scope(RESPONSE_MSG["FAILED"]["INSUFFICIENT_PERMISSION"])
        else:
            return fn(*args, **kwargs)

    return wrapper
#end def

def refresh_token_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # define header schema
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers', required=True)
        header = parser.parse_args()

        # accessing token from header
        auth_header = header["Authorization"]
        token = auth_header.split(" ")[1]

        response = AuthServices.current_login_user(token)

        if response["status"] != "SUCCESS":
            return bad_request(response["data"])
        #end if

        if response["data"]["token_type"] != "REFRESH":
            return method_not_allowed(RESPONSE_MSG["FAILED"]["REFRESH_TOKEN_ONLY"])
        else:
            return fn(*args, **kwargs)

    return wrapper
#end def

def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # define header schema
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers', required=True)
        header = parser.parse_args()

        # accessing token from header
        auth_header = header["Authorization"]
        token = auth_header.split(" ")[1]

        response = AuthServices.current_login_user(token)

        if response["status"] != "SUCCESS":
            return bad_request(response["data"])
        #end if

        return fn(*args, **kwargs)

    return wrapper
#end def

def get_token_payload():
    # define header schema
    parser = reqparse.RequestParser()
    parser.add_argument('Authorization', location='headers', required=True)
    header = parser.parse_args()

    # accessing token from header
    auth_header = header["Authorization"]
    token = auth_header.split(" ")[1]

    response = AuthServices.current_login_user(token)

    if response["status"] != "SUCCESS":
        return bad_request(response["data"])
    #end if

    return response["data"]
#end def

def get_current_token():
    # define header schema
    parser = reqparse.RequestParser()
    parser.add_argument('Authorization', location='headers', required=True)
    header = parser.parse_args()

    # accessing token from header
    auth_header = header["Authorization"]
    token = auth_header.split(" ")[1]

    return token
#end def
