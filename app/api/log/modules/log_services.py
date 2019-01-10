""" 
    Log Services
    _________________
    This services module to handle all incoming and outgoing log
"""
import traceback
import jwt

from app.api            import db
from app.api.models     import ExternalLog
from app.api.serializer import ExternalLogSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class LogServices:
    """ Log Services Class"""

    def show(self, params):
        """
            Function to show all log
            args:
                params -- parameter
        """
        response = {}

        ext_log = ExternalLog.query.all()
        response["data"] = ExternalLogSchema(many=True).dump(ext_log).data
        return response
        #end def
#end class
