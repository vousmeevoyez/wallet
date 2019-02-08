from os import path
import json
import csv

from flask_testing  import TestCase
from unittest.mock import Mock, patch

from manage         import app, init
from app.api        import db
# configuration
from app.config import config
# models
from app.api.models import User
from app.api.models import Role
from app.api.models import VaType
from app.api.models import PaymentChannel
from app.api.models import Bank

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

        role = Role(
            description="USER",
        )
        db.session.add(role)
        db.session.commit()

        # add dummy user
        user = User(
            username='jenniebp',
            name='jennie',
            email='jennie@bp.com',
            phone_ext='62',
            phone_number='82219644314',
            role_id=role.id,
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        self.user = user
#end class
