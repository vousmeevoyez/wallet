"""
    Log Routes
    _____________________
    Module that handler routes for log
"""
from functools import wraps
import traceback

from flask_restplus     import Resource, reqparse

from app.api.log                      import api
from app.api.serializer               import UserSchema
from app.api.request_schema           import AuthRequestSchema
from app.api.errors                   import bad_request, internal_error
from app.api.authentication.decorator import token_required, get_current_token, get_token_payload
from app.api.config                   import config
from app.api.log.modules.log_services import LogServices

request_schema = AuthRequestSchema.parser

RESPONSE_MSG = config.Config.RESPONSE_MSG

@api.route("/")
class LogRoutes(Resource):
    """ Log Routes"""
    # authenticate the user and return access token
    def get (self):
        """ handle get method request"""
        response = LogServices().show({})
        return response
#end def
