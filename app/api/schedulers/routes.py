"""
    Scheduler Routes
    _______________
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods
from datetime import datetime, timedelta
from flask_restplus import Resource
from marshmallow import ValidationError
# celery
from app.api import celery
# task
from task.payment.tasks import PaymentTask

from app.api.schedulers import api
#serializer
from app.api.serializer import *
# request schema
from app.api.request_schema import *
# scheduler modules
from app.api.schedulers.modules.scheduler_services import SchedulerServices
# authentication
from app.api.auth.decorator import token_required
from app.api.auth.decorator import get_token_payload
from app.api.auth.decorator import admin_required
# exceptions
from app.api.error.http import *
# configuration
from app.config import config

class BaseRoutes(Resource):
    error_response = config.Config.ERROR_CONFIG

@api.route('/')
class SchedulerRoutes(BaseRoutes):
    """
        Scheduler
        /scheduler
    """
    #@token_required
    def post(self):
        """ Endpoint for creating payment plan """
        executed_at = datetime.now() + timedelta(seconds=60)
        print(executed_at)
        response = SchedulerServices.add("greet_user", "Hi Jessica Krystal",
                                         executed_at)
        return response
    #end def

    def get(self):
        """ Endpoint for creating payment plan """
        response = SchedulerServices.show_all()
        return response
    #end def
#end class

@api.route('/<string:job_id>')
class SchedulerInfoRoutes(BaseRoutes):
    """
        Scheduler
        /scheduler
    """
    #@token_required
    def delete(self, job_id):
        """ Endpoint for removing schedule """
        response = SchedulerServices.remove(job_id)
        return response
    #end def
#end class
