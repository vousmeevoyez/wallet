"""
    Log Routes
    _____________________
    Module that handler routes for log
"""
# core
from flask_restplus import Resource, reqparse
# namespace
from app.api.logs import api
# services
from app.api.logs.modules.log_services import LogServices

@api.route("/")
class LogRoutes(Resource):
    """
        Logs
        /logs
    """
    def get (self):
        """ Endpoint for return all external log """
        response = LogServices().show({})
        return response
#end def
