"""
    Scheduler Routes
    _______________
"""
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods
from datetime import datetime, timedelta

from app.api.core import Routes

from app.api.schedulers import api

# request schema
from app.api.request_schema import *

# scheduler modules
from app.api.schedulers.modules.scheduler_services import SchedulerServices


@api.route("/")
class SchedulerRoutes(Routes):
    """
        Scheduler
        /scheduler
    """

    # @token_required
    def post(self):
        """ Endpoint for creating payment plan """
        executed_at = datetime.now() + timedelta(seconds=60)
        response = SchedulerServices.add(
            "greet_user", "Hi Jessica Krystal", executed_at
        )
        return response

    # end def

    def get(self):
        """ Endpoint for creating payment plan """
        response = SchedulerServices.show_all()
        return response

    # end def


# end class


@api.route("/<string:job_id>")
class SchedulerInfoRoutes(Routes):
    """
        Scheduler
        /scheduler
    """

    # @token_required
    def delete(self, job_id):
        """ Endpoint for removing schedule """
        response = SchedulerServices.remove(job_id)
        return response

    # end def


# end class
