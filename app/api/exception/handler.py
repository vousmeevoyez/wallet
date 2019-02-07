from app.api.exception import api

from app.api.http_response import *

from app.api.exception.general import SerializeError
from app.api.exception.general import RecordNotFoundError
from app.api.exception.general import CommitError

# authentication
from app.api.exception.authentication import TokenError
from app.api.exception.authentication import InvalidCredentialsError
from app.api.exception.authentication import MethodNotAllowedError
from app.api.exception.authentication import InvalidAuthorizationError
from app.api.exception.authentication import InsufficientScopeError

@api.errorhandler(SerializeError)
def handle_serialize_error(error):
    """ handle raised serialize error from routes """
    return bad_request("INVALID_PARAMETER", error.msg, error.details)

@api.errorhandler(RecordNotFoundError)
def handle_not_existed_entry(error):
    """ handle raised not existed entry error from routes """
    if error.header is None:
        header = "RECORD_NOT_FOUND"
    else:
        header = error.header

    return request_not_found(header, error.msg, None)

@api.errorhandler(CommitError)
def handle_commit_error(error):
    """ handle commit error """
    if error.header is None:
        header = "DUPLICATE_ENTRY"
    else:
        header = error.header

    if error.details is not None:
        details = error.details
    else:
        details = None

    return unprocessable_entity(header, error.msg, details)

"""
    AUTHENTICATION EXCEPTION HANDLER
"""
@api.errorhandler(TokenError)
def handle_token_error(error):
    """ handle raised token error routes """
    return unauthorized(None, error.msg, None)

@api.errorhandler(InsufficientScopeError)
def handle_insufficient_scope(error):
    """ handle raised invalid credentials from routes """
    return insufficient_scope(None, error.msg, None)

@api.errorhandler(InvalidCredentialsError)
def handle_invalid_credentials(error):
    """ handle raised invalid credentials from routes """
    return unauthorized(None, error.msg, None)

@api.errorhandler(MethodNotAllowedError)
def handle_method_not_allowed_error(error):
    """ handle raised when accss token used in refresh routes """
    return method_not_allowed(None, error.msg, None)

@api.errorhandler(InvalidAuthorizationError)
def handle_invalid_authorization_error(error):
    """ handle invalid authorization error routes """
    return unauthorized(None, error.msg, None)

"""
    USER EXCEPTION HANDLER
"""
