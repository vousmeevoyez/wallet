import sys
import json

from datetime import datetime

sys.path.append("../")
sys.path.append("../app")
sys.path.append("../app/common")

import unittest
from unittest.mock import Mock, patch

from app            import create_app, db
from app.common     import helper
from app.config     import config

class TestConfig(config.Config):
    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class TestSMSHelper(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_send_sms(self):
        result = helper.SmsHelper().send_sms("6281219644314", "FORGOT_PIN", "123456")
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main(verbosity=2)

