"""
    Auth Decorator
    ________________
    this is module that contain various decorator to protect various endpoint
"""
from flask import request
from functools import wraps

from flask_restplus import reqparse

from app.api.authentication.modules.auth_services import AuthServices

from app.api.exception.authentication.exceptions import ParseTokenError
from app.api.exception.authentication.exceptions import TokenError

from app.api.http_response import bad_request
from app.api.http_response import unauthorized
from app.api.http_response import insufficient_scope
from app.api.http_response import method_not_allowed

from app.config  import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

def _parse_token():
    """ parse token from header """
    parser = reqparse.RequestParser()
    parser.add_argument('Authorization', location='headers', required=True)
    header = parser.parse_args(strict=True)

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

# CUSTOM DECORATOR
def admin_required(fn):
    """
        decorator to only allow admin access this function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        try:
            token = _parse_token()
        except ParseTokenError as error:
            return bad_request(error.msg)
        #end def

        try:
            response = AuthServices.current_login_user(token)
        except TokenError as error:
            return unauthorized(error.msg)
        #end try
        if response["role"] != "ADMIN":
            return insufficient_scope()
        else:
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
        try:
            token = _parse_token()
        except ParseTokenError as error:
            return bad_request(error.msg)
        #end def

        try:
            response = AuthServices.current_login_user(token)
        except TokenError as error:
            return unauthorized(error.msg)

        if response["token_type"] != "REFRESH":
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
        except ParseTokenError as error:
            return bad_request(error.msg)
        #end try
        try:
            response = AuthServices.current_login_user(token)
        except TokenError as error:
            return unauthorized(error.msg)
        #end try
        return fn(*args, **kwargs)
    return wrapper
#end def

def get_token_payload():
    """ get token payload """
    # define header schema

    try:
        token = _parse_token()
    except ParseTokenError as error:
        return bad_request(error.msg)
    #end try
    try:
        response = AuthServices.current_login_user(token)
    except TokenError as error:
        return unauthorized(error.msg)
    #end try
    return response
#end def

def get_current_token():
    """ get current token from headers """
    # define header schema
    try:
        token = _parse_token()
    except ParseTokenError as error:
        return bad_request(error.msg)
    return token
#end def
