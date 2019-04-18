"""
    Scheduler Services
    _________________
"""
#pylint: disable=no-self-use
#pylint: disable=import-error
#pylint: disable=bad-whitespace
#pylint: disable=invalid-name
from datetime import datetime
from sqlalchemy.exc import IntegrityError
# scheduler
from app.api import scheduler
# database
from app.api import db
#models
from app.api.models import *
# exceptions
from app.api.error.http import *
#http response
from app.api.http_response import *
# serializer
from app.api.serializer import UserSchema
# utility
from app.api.utility.utils import validate_uuid
# task
from task.payment.tasks import PaymentTask

def greet_user(text):
    """ testing function to greet user at some time"""
    print("{} at {}".format(text, datetime.now()))
# end def

class SchedulerServices:
    """ Scheduler Services"""
    @staticmethod
    def add(task_name, task_arg, execute_at):
        """
            Add Schedule Job
        """
        job = scheduler.add_job(
            task_name,
            trigger='date',
            next_run_time=execute_at,
            args=[task_arg]
        )
        return accepted({"message" : "Task Scheduled!"})
    # end def

    @staticmethod
    def show_all():
        """
            Get All Schedule Job
        """
        scheduled_jobs = []
        for scheduled_job in scheduler.get_jobs():
            scheduled_jobs.append({
                "id" : scheduled_job.id,
                "function" : str(scheduled_job.func),
                "next_run_time" : str(scheduled_job.next_run_time)
            })
        # end for
        return scheduled_jobs
    # end def

    @staticmethod
    def remove(task_id):
        """
            Remove Schedule Job
        """
        job = scheduler.remove_job(
           task_id
        )
        return accepted({"message" : "Task Removed!"})
    # end def
#end class
