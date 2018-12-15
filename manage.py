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

app = create_app(os.getenv("ENV") or 'dev')
app.register_blueprint(blueprint, url_prefix="/api/v1")

app.app_context().push()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def run():
    app.run()
#end def

@manager.command
def test():
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1
#end def

@manager.command
def init():
    # create necessary role for wallet system
    role_list = _create_role()
    # create admin for wallet system
    _create_admin(role_list["ADMIN"])
    # import necessary bank data for wallet system
    _import_bank_csv()
    # create necessary va type
    _create_va_type()
#end def

def make_shell_context():
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
#end def

manager.add_command("shell", Shell(make_context=make_shell_context))

# INIT UTILITY FUNCTION
def _create_role():
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

def _create_admin(role_id):
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

def _import_bank_csv():
    FILEPATH = "data/bank_list.csv"
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

def _create_va_type():
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

if __name__ == "__main__":
    manager.run()

