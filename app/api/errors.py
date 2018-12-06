from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    payload = {}

    if message:
        payload["errors"] = message
    else:
        payload["errors"] = HTTP_STATUS_CODES.get(status_code, 'Unknown Error'),
    #end if
    response = payload
    return response, status_code
#end def

"""
    4xx Client Error
"""

def bad_request(message=None):
    return error_response(400, message)
#end def

def request_not_found(message=None):
    return error_response(404, message)
#end def

def insufficient_scope(message=None):
    return error_response(403, message)
#end def

def method_not_allowed(message=None):
    return error_response(405, message)
#end def

"""
    5xx Server Error
"""

def internal_error(message=None):
    return error_response(500, message)
#end def

def bad_gateway(message=None):
    return error_response(502, message)
#end def

def service_unavailable(message=None):
    return error_response(503, message)
#end def
