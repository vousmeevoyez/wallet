from os import path
import json
import csv

from flask_testing  import TestCase
from unittest.mock import Mock, patch

from manage         import app
from app.api        import db
from app.api.config import config
from app.api.models import User, Role, VaType, Bank, PaymentChannel

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
        self._create_va_type()
        self._import_bank_csv()
        self._create_payment_channel()

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

    def _create_va_type(self):
        # REGISTER VA TYPE HERE
        va_credit = VaType(
            key="CREDIT"
        )
        # debit
        va_debit = VaType(
            key="DEBIT"
        )
        db.session.add(va_debit)
        db.session.add(va_credit)
        db.session.commit()
    #end def

    def _create_payment_channel(self):
        bni = Bank.query.filter_by(code="009").first()
        payment_channel = PaymentChannel(
            name="BNI Virtual Account",
            key="BNI_VA",
            channel_type="VIRTUAL_ACCOUNT",
            bank_id=bni.id
        )
        db.session.add(payment_channel)
        db.session.commit()
    #end def

    def _import_bank_csv(self):
        base_path = path.abspath("data")
        FILEPATH = base_path + "/bank_list.csv"
        with open(FILEPATH, "r") as f:
            csv_reader = csv.DictReader(f)
            line = 0
            for row in csv_reader:
                if line > 0:
                    bank=Bank(
                        name=row["bank_name"],
                        code=row["bank_code"],
                    )
                    db.session.add(bank)
                    db.session.commit()
                #end if
                line += 1
            #end for
        #end with
    #end def
#end class
