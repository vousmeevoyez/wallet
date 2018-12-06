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

    # create admin account here
    admin = User(
        username="MODANAADMIN",
        name="Modana Admin",
        phone_ext="62",
        phone_number="81212341234",
        email="admin@modana.id",
        role_id=admin_role.id
    )
    admin.set_password("password")
    db.session.add(admin)

    # REGISTER BANK HERE
    bni=Bank(
        key="BNI",
        name="Bank BNI",
        code="009",
    )
    db.session.add(bni)

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

def make_shell_context():
    return {
            'app'            : app,
            'db'             : db,
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

if __name__ == "__main__":
    manager.run()

