"""
    Manage
    ___________________
    This is flask application entry
"""
import csv
import os
import unittest

from flask_migrate  import Migrate, MigrateCommand
from flask_script   import Manager, Shell

from app        import blueprint
from app.api    import create_app, db

#import model here
from app.api        import models
from app.api.models import *

app = create_app(os.getenv("ENVIRONMENT") or 'dev')
app.register_blueprint(blueprint, url_prefix="/api/v1")

app.app_context().push()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def run():
    """ function to start flask apps"""
    host = os.getenv("HOST") or '127.0.0.1'
    app.run(host=host)

@manager.command
def test():
    """ function to run unittest"""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def init():
    """ create init function here """

    # create necessary role for wallet system
    role_list = _create_role()
    # create admin for wallet system
    _create_admin(role_list["ADMIN"])
    # import necessary bank data for wallet system
    _import_bank_csv()
    # create necessary va type
    _create_va_type()
    # create payment_channel
    _create_payment_channel()

def make_shell_context():
    """ create shell context here"""
    return {
        'app'            : app,
        'db'             : db,
        'Bank'           : Bank,
        'BankAccount'    : BankAccount,
        'Role'           : Role,
        'Wallet'         : Wallet,
        'VirtualAccount' : VirtualAccount,
        'Transaction'    : Transaction,
        'ExternalLog'    : ExternalLog,
        'ForgotPin'      : ForgotPin,
        'User'           : User
    }

manager.add_command("shell", Shell(make_context=make_shell_context))

# INIT UTILITY FUNCTION
def _create_role():
    roles = {
        "ADMIN" : None,
        "USER"  : None,
    }

    role = Role.query.all()
    if not role:
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
        roles["USER"] = user_role.id
    else:
        for i in role:
            if i.description == "ADMIN":
                roles["ADMIN"] = i.id
            else:
                roles["USER"] = i.id
    return roles

def _create_admin(role_id):
    # only create admin when there are no admin yet
    user = User.query.count()
    if user == 0:
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

def _import_bank_csv():
    # only imoprt the bank when there are none
    bank_list = Bank.query.all()
    if not bank_list:
        file_path = "data/bank_list.csv"
        with open(file_path, "r") as files:
            csv_reader = csv.DictReader(files)
            line = 0
            for row in csv_reader:
                if line > 0:
                    bank = Bank(
                        name=row["bank_name"],
                        code=row["bank_code"],
                    )
                    db.session.add(bank)
                    db.session.commit()
                line += 1

def _create_va_type():
    # only create va type when there are none
    va_type = VaType.query.count()
    if va_type == 0:
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

def _create_payment_channel():
    # only create payment if there are none
    payment_channel = PaymentChannel.query.count()
    if payment_channel == 0:
        bni = Bank.query.filter_by(code="009").first()
        payment_channel = PaymentChannel(
            name="BNI Virtual Account",
            key="BNI_VA",
            channel_type="VIRTUAL_ACCOUNT",
            bank_id=bni.id
        )
        db.session.add(payment_channel)
        db.session.commit()

if __name__ == "__main__":
    manager.run()
