"""
    Auth Decorator
    ________________
    this is module that contain various decorator to protect various endpoint
"""
from flask import request
from functools import wraps

from flask_restplus import reqparse

from app.api.authentication.modules.auth_services import AuthServices

from app.api.exception.authentication.exceptions import InvalidAuthHeaderError
from app.api.exception.authentication.exceptions import EmptyAuthHeaderError

from app.api.errors  import bad_request
from app.api.errors  import internal_error
from app.api.errors  import insufficient_scope
from app.api.errors  import method_not_allowed

from app.api.config  import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

def _parse_token():
    """ parse token from header """
    parser = reqparse.RequestParser()
    parser.add_argument('Authorization', location='headers', required=True)
    header = parser.parse_args(strict=True)

    # accessing token from header
    auth_header = header["Authorization"]
    if auth_header == "":
        raise EmptyAuthHeaderError
    #end if

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        raise InvalidAuthHeaderError
    #end def
    return token
#end def

# CUSTOM DECORATOR
def admin_required(fn):
    """
        decorator to only allow admin access this function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        try:
            token = _parse_token()
        except EmptyAuthHeaderError:
            return bad_request("Empty Authorization Headers")
        #end def
        except InvalidAuthHeaderError:
            return bad_request("Invalid Authorization Header")
        #end def

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
    """
        only allow refresh token for certain routes
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            token = _parse_token()
        except EmptyAuthHeaderError:
            return bad_request("Empty Authorization Headers")
        #end def
        except InvalidAuthHeaderError:
            return bad_request("Invalid Authorization Header")
        #end def

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
    """
        protect routes with token
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        try:
            token = _parse_token()
        except EmptyAuthHeaderError:
            return bad_request("Empty Authorization Headers")
        #end def
        except InvalidAuthHeaderError:
            return bad_request("Invalid Authorization Header")
        #end def

        response = AuthServices.current_login_user(token)

        if response["status"] != "SUCCESS":
            return bad_request(response["data"])
        #end if

        return fn(*args, **kwargs)

    return wrapper
#end def

def get_token_payload():
    """ get token payload """
    # define header schema

    try:
        token = _parse_token()
    except EmptyAuthHeaderError:
        return bad_request("Empty Authorization Headers")
    #end def
    except InvalidAuthHeaderError:
        return bad_request("Invalid Authorization Header")
    #end def

    response = AuthServices.current_login_user(token)

    if response["status"] != "SUCCESS":
        return bad_request(response["data"])
    #end if

    return response["data"]
#end def

def get_current_token():
    """ get current token from headers """
    # define header schema
    try:
        token = _parse_token()
    except EmptyAuthHeaderError:
        return bad_request("Empty Authorization Headers")
    #end def
    except InvalidAuthHeaderError:
        return bad_request("Invalid Authorization Header")
    #end def

    return token
#end def
