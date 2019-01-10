from os import path
import json
import csv

from flask_testing  import TestCase
from unittest.mock import Mock, patch

from manage         import app, init
from app.api        import db
from app.api.config import config
from app.api.models import User, Role, VaType, Bank, PaymentChannel

TEST_CONFIG = config.TestingConfig

class BaseTestCase(TestCase):
    """ This is Base Tests """

    user = None

    def create_app(self):
        app.config.from_object(TEST_CONFIG)
        return app

    def setUp(self):
        db.create_all()
        # wrap everything for initialization here
        self._init_test()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _init_test(self):
        init()
#end class
