"""
    Utility Routes
    _____________________
    Module that handler http request for utility
"""
# core
from app.lib.core import Routes

# namespace
from app.api.utility import api

# services
from app.api.utility.modules.health_services import HealthServices


@api.route("/health")
class UtilityRoutes(Routes):
    """
        utility health check via HTTP
        /utility/health
    """

    def get(self):
        """ Endpoint for checking all health """
        response = HealthServices().check()
        return response
