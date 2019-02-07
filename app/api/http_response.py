""" 
    HTTP Response
    __________
    This module to handle HTTP Success & Error code
"""
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
"""
    2xx Success
"""
def no_content():
    """
        Function to return 204 HTTP success message
    """
    return ('', 204)
#end def

def created(data=None, message=None):
    """
        Function to return 201 HTTP success message
    """
    response = {}

    if data is not None:
        response["data"] = data

    if message is not None:
        response["message"] = message

    return (response, 201)
#end def

def accepted(message=None):
    """
        Function to return 202 HTTP success message
    """
    response = {}

    if message is not None:
        response["message"] = message

    return (response, 202)
#end def

def error_response(status_code, error, message, details):
    """
    Function to set status code and error message

    args:
        status_code -- HTTP Status Code (400 , 404, 405, etc...)
        message -- Error message to be returned (optional)
    """
    response = {
        "error"   : error,
        "message" : message,
        "details" : details
    }

    if message is None:
        del response["message"]

    if details is None:
        del response["details"]

    return (response, status_code)
#end def

"""
    4xx Client Error
"""

def bad_request(error=None, message=None, details=None):
    """
    Function to return 400 HTTP error message

    args:
        error_header -- Error header to be returned (optional)
        message -- Error message to be returned (optional)
    """
    if error is None:
        error = "INVALID_REQUEST"

    return error_response(400, error, message, details)
#end def

def unauthorized(error=None, message=None, details=None):
    """
    Function to return 401 HTTP error message

    args:
        error_header -- Error header to be returned (optional)
        message -- Error message to be returned (optional)
    """
    if error is None:
        error = "AUTHENTICATION_FAILURE"
    return error_response(401, error, message, details)
#end def

def request_not_found(error=None, message=None, details=None):
    """
    Function to return 404 HTTP error message

    args:
        error_header -- Error header to be returned (optional)
        message -- Error message to be returned (optional)
    """
    if error is None:
        error = "RESOURCE_NOT_FOUND"
    return error_response(404, error, message, details)
#end def

def insufficient_scope(error=None, message=None, details=None):
    """
    Function to return 403 HTTP error message

    args:
        error_header -- Error header to be returned (optional)
        message -- Error message to be returned (optional)
    """
    if error is None:
        error = "NOT_AUTHORIZED"
    return error_response(403, error, message, details)
#end def

def unprocessable_entity(error=None, message=None, details=None):
    """
    Function to return 422 HTTP error message

    args:
        error_header -- Error header to be returned (optional)
        message -- Error message to be returned (optional)
    """
    if error is None:
        error = "UNPROCCESSABLE_ENTITY"
    return error_response(422, error, message, details)
#end def

def method_not_allowed(error=None, message=None, details=None):
    """ Function to return 405 HTTP error message
        error_header -- Error header to be returned (optional)
        message -- Error message to be returned (optional)
    """
    if error is None:
        error = "METHOD_NOT_SUPPORTED"
    return error_response(405, error, message, details)
#end def

"""
    5xx Server Error
"""
def internal_error(error=None, message=None, details=None):
    """
    Function to return 500 HTTP error message

    args:
        message -- Error message to be returned (optional)
    """
    return error_response(500, error, message, details)
#end def

def bad_gateway(error=None, message=None, details=None):
    """
    Function to return 502 HTTP error message

    args:
        message -- Error message to be returned (optional)
    """
    return error_response(502, error, message, details)
#end def

def service_unavailable(error=None, message=None, details=None):
    """
    Function to return 503 HTTP error message

    args:
        message -- Error message to be returned (optional)
    """
    return error_response(503, error, message, details)
#end def
