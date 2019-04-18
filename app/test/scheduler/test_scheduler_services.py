"""
    Test Scheduler Services
"""
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from app.api import db

from app.test.base import BaseTestCase

from app.api.models import *

from app.api.utility.utils import Sms

from app.api.utility.modules.sms_services import SmsError

from app.api.error.http import *

from app.api.scheduler.modules.scheduler_services import SchedulerServices

class TestSchedulerServices(BaseTestCase):
    """ Test Class for Scheduler Services"""

    def test_add_schedule(self):
        executed_at = datetime.now() + timedelta(seconds=10)
        result = SchedulerServices().add("greet_user", "Hi Jessica Jung",
                                         executed_at)
        print(result)

    def test_show_all_schedule(self):
        executed_at = datetime.now() + timedelta(seconds=10)
        result = SchedulerServices.show_all()
        print(result)
