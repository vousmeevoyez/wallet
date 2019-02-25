from flask_testing  import TestCase

from unittest.mock import Mock, patch

from manage  import init
from task.worker import app

from app.api import db
# configuration
from app.config import config
# models
from app.api.models import *

TEST_CONFIG = config.TestingConfig

class BaseTestCase(TestCase):

    user = None

    """ This is Base Tests """
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
            username='testtest',
            name='jennie',
            email='testtest@bp.com',
            phone_ext='62',
            phone_number='8212341234123',
            role_id=role.id,
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        self.user = user
        
        wallet = Wallet(user_id=user.id)
        db.session.add(wallet)
        db.session.commit()

        wallet2 = Wallet()
        db.session.add(wallet2)
        db.session.commit()

        # add some balance here for test case
        source = wallet
        source.add_balance(100)
        db.session.commit()

        # add some balance here for test case
        destination = wallet2
        destination.add_balance(100)
        db.session.commit()

        self.source = source
        self.destination = destination
#end class
