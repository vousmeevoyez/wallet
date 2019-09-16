"""
    Log Routes
    _____________________
    Module that handler routes for log
"""
# core
from app.api.core import Routes

# namespace
from app.api.logs import api

# services
from app.api.logs.modules.log_services import LogServices


@api.route("/")
class LogRoutes(Routes):
    """
        Logs
        /logs
    """

    def get(self):
        """ Endpoint for return all external log """
        response = LogServices().show({})
        return response

    # end def


# end def
