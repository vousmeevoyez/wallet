"""
    Auth Decorator
    ________________
    this is module that contain various decorator to protect various endpoint
"""
from functools import wraps
from flask import request

from flask_restplus import reqparse

from app.api.authentication.modules.auth_services import AuthServices

from app.api.models import User

from app.api.exception.authentication import ParseTokenError
from app.api.exception.authentication import TokenError
from app.api.exception.authentication import InvalidAuthorizationError
from app.api.exception.authentication import InsufficientScopeError
from app.api.exception.authentication import MethodNotAllowedError

from app.api.http_response import bad_request
from app.api.http_response import unauthorized
from app.api.http_response import insufficient_scope
from app.api.http_response import method_not_allowed

from app.config  import config

def _parse_token():
    """ parse token from header """
    parser = reqparse.RequestParser()
    parser.add_argument('Authorization', location='headers', required=True)
    header = parser.parse_args()

    # accessing token from header
    auth_header = header["Authorization"]
    if auth_header == "":
        raise ParseTokenError("Empty Auth Header")
    #end if

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        raise ParseTokenError("Invalid Auth Header")
    #end def
    return token
#end def

def get_token_payload():
    """ get token payload """
    # define header schema

    try:
        token = _parse_token()
    except ParseTokenError as error:
        raise InvalidAuthorizationError(error.msg)
    #end def

    try:
        response = AuthServices._current_login_user(token)
    except TokenError as error:
        raise InvalidAuthorizationError(error.msg)
    #end try
    return response
#end def

# CUSTOM DECORATOR
def admin_required(fn):
    """
        decorator to only allow admin access this function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        response = get_token_payload()
        user = response["user"]

        # check permission here
        if user.role.description != "ADMIN":
            raise InsufficientScopeError("Require admin permission")

        return fn(*args, **kwargs)
        #end if
    return wrapper
#end def

def refresh_token_only(fn):
    """
        only allow refresh token for certain routes
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        response = get_token_payload()

        if response["token_type"] != "REFRESH":
            raise MethodNotAllowedError("Refresh token only")
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

        response = get_token_payload()

        return fn(*args, **kwargs)
    return wrapper
#end def

def get_current_token():
    """ get current token from headers """
    # define header schema
    try:
        token = _parse_token()
    except ParseTokenError as error:
        raise InvalidAuthorizationError(error.msg)
    #end def
    return token
#end def
