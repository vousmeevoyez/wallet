"""
    Auth Decorator
    ________________
    this is module that contain various decorator to protect various endpoint
"""
# standard
from functools import wraps
# external
from flask_restplus import reqparse
# local
from app.api.auth.modules.auth_services import AuthServices
from app.api.error.http import BadRequest, InsufficientScope, MethodNotAllowed
from app.api.error.message import RESPONSE as error_response


class ParseError(Exception):
    """ raised when failed parsing token from header"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def _parse_token():
    """ parse token from header """
    parser = reqparse.RequestParser()
    parser.add_argument('Authorization', location='headers', required=True)
    header = parser.parse_args()

    # accessing token from header
    auth_header = header["Authorization"]
    if auth_header == "":
        raise ParseError("Empty Auth Header")
    #end if

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        raise ParseError("Invalid Auth Header")
    #end try
    return token
#end def

def get_token_payload():
    """ get token payload """
    # define header schema

    try:
        token = _parse_token()
    except ParseError as error:
        raise BadRequest(error_response["BAD_AUTH_HEADER"], error.message)
    #end try

    response = AuthServices().current_login_user(token)
    return response
#end def

# CUSTOM DECORATOR
def admin_required(func):
    """ decorator to only allow admin access this function """
    @wraps(func)
    def wrapper(*args, **kwargs):

        response = get_token_payload()
        user = response["user"]

        # check permission here
        if user.role.description != "ADMIN":
            raise InsufficientScope(error_response["ADMIN_REQUIRED"]["TITLE"],
                                    error_response["ADMIN_REQUIRED"]["MESSAGE"])
        # end if

        return func(*args, **kwargs)
        #end if
    return wrapper
#end def

def refresh_token_only(func):
    """ only allow refresh token for certain routes """
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = get_token_payload()

        if response["token_type"] != "REFRESH":
            raise MethodNotAllowed("Refresh token only")
        else:
            return func(*args, **kwargs)
        # end if
    # end def
    return wrapper
#end def

def token_required(func):
    """ protect routes with token """
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = get_token_payload()
        return func(*args, **kwargs)
    # end def
    return wrapper
#end def

def get_current_token():
    """ get current token from headers """
    # define header schema
    try:
        token = _parse_token()
    except ParseError as error:
        raise BadRequest(error_response["BAD_AUTH_HEADER"], error.message)
    #end try
    return token
#end def

################ PATCH ########################
def _parse_key():
    """ parse api key from header """
    parser = reqparse.RequestParser()
    parser.add_argument('X-Api-Key', location='headers', required=True)
    header = parser.parse_args()

    # accessing token from header
    api_key_header = header["X-Api-Key"]
    if api_key_header == "":
        raise ParseError("Empty Api Key Header")
    #end if
    return api_key_header
#end def

################ PATCH ########################
def api_key_required(func):
    """ protect routes with api key """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = _parse_key()
        except ParseError as error:
            raise BadRequest(error_response["BAD_AUTH_HEADER"], error.message)
        else:
            result = AuthServices.check_key(result)
        # end try
        return func(*args, **kwargs)
    # end def
    return wrapper
#end def
