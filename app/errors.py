from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    payload = {
        "status_code"    : status_code,
        "status_message" : HTTP_STATUS_CODES.get(status_code, 'Unknown Error'),
        "data" : ""
    }
    if message:
        payload["data"] = message
    response = jsonify(payload)
    #response.status_code = status_code

    return response

def bad_request(message=None):
    return error_response(400, message)

def request_not_found(message=None):
    return error_response(404, message)

def forbidden_request(message=None):
    return error_response(403, message)

def method_not_allowed(message=None):
    return error_response(405, message)

def internal_error(message=None):
    return error_response(500, message)

