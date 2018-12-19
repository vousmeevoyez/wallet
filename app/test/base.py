import json

from flask_testing  import TestCase
from unittest.mock import Mock, patch

from manage         import app
from app.api        import db
from app.api.config import config
from app.api.models import User, Role

TEST_CONFIG = config.TestingConfig

class BaseTestCase(TestCase):
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
        roles = self._create_role()
        self._create_admin(roles["ADMIN"])

    def _create_role(self):
        roles = {
            "ADMIN" : None,
            "USER"  : None,
        }

        # create record for user role here
        admin_role = Role(
            description="ADMIN"
        )
        db.session.add(admin_role)

        user_role = Role(
            description="USER"
        )
        db.session.add(user_role)
        db.session.commit()

        roles["ADMIN"] = admin_role.id
        roles["USER" ] = user_role.id

        return roles
    #end def

    def _create_admin(self, role_id):
        # create admin account here
        admin = User(
            username="MODANAADMIN",
            name="Modana Admin",
            phone_ext="62",
            phone_number="81212341234",
            email="admin@modana.id",
            role_id=role_id
        )
        admin.set_password("password")
        db.session.add(admin)
        db.session.commit()
    #end def
