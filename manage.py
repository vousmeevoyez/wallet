"""
    Manage
    ___________________
    This is flask application entry
"""
# standard
import csv
import os
import unittest

# external
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

# local
from app import blueprint
from app.api import create_app, db

# import model here
from app.api import models
from app.api.models import *
from app.api.virtual_accounts.modules.va_services import bulk_update_va

from task.quota.tasks import QuotaTask

app = create_app(os.getenv("ENVIRONMENT") or "dev")
app.register_blueprint(blueprint, url_prefix="/api/v1")

app.app_context().push()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command("db", MigrateCommand)


@manager.command
def run():
    """ function to start flask apps"""
    host = os.getenv("HOST") or "127.0.0.1"
    app.run(host=host)


@manager.command
def test():
    """ function to run unittest"""
    test_dir = ["app/test", "task/test"]
    tests = unittest.TestSuite()
    for test in test_dir:
        test_suite = unittest.TestLoader().discover(test, pattern="test*.py")
        tests.addTest(test_suite)
    # end for
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
    # create necessary transaction type
    _create_transaction_type()
    # create necessary transaction notes
    _create_transaction_note()
    # create payment_channel
    _create_payment_channel()
    # create api key
    _create_api_key()
    _create_quota()


@manager.command
def update_va():
    """ create init function here """
    bulk_update_va()


def make_shell_context():
    """ create shell context here"""
    return {
        "app": app,
        "db": db,
        "Bank": Bank,
        "BankAccount": BankAccount,
        "Role": Role,
        "Wallet": Wallet,
        "VirtualAccount": VirtualAccount,
        "Transaction": Transaction,
        "Log": Log,
        "ForgotPin": ForgotPin,
        "Payment": Payment,
        "PaymentChannel": PaymentChannel,
        "PaymentPlan": PaymentPlan,
        "Plan": Plan,
        "User": User,
    }


manager.add_command("shell", Shell(make_context=make_shell_context))

# INIT UTILITY FUNCTION
def _create_role():
    roles = {"ADMIN": None, "USER": None}

    role = Role.query.all()
    if not role:
        # create record for user role here
        admin_role = Role(description="ADMIN")
        db.session.add(admin_role)

        user_role = Role(description="USER")
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
            phone_number="6666666667",
            email="admin@modana.id",
            role_id=role_id,
        )
        admin.set_password("password")
        db.session.add(admin)
        db.session.commit()


def read_file(file_path):
    # read file from file path and return iterator
    with open(file_path, "r") as files:
        csv_reader = csv.reader(files, delimiter=";")
        line = 0
        for row in csv_reader:
            # skip headers
            if line > 0:
                yield row
            line += 1


def find_bank_row(bank_code, file_path):
    # find bank data from csv using bank code
    rows = read_file(file_path)
    for row in rows:
        if row[0] == bank_code:
            return row
        else:
            raise ValueError


def _import_bank_csv():
    # only imoprt the bank when there are none
    bank_list = Bank.query.all()
    # if there's nothing in the db we load everything
    if not bank_list:
        datas = read_file("data/bank_list.csv")
        for data in datas:
            bank = Bank(code=data[0], name=data[2], rtgs=data[1])
            db.session.add(bank)
            db.session.commit()
    # if already some data we update or add new entry
    else:
        datas = read_file("data/bank_list.csv")
        for data in datas:
            bank = Bank.query.filter_by(code=data[0]).first()
            if bank is None:
                new_bank = Bank(code=data[0], name=data[2], rtgs=data[1])
                db.session.add(new_bank)
                db.session.commit()
            else:
                bank.name = data[2]
                bank.rtgs = data[1]
                db.session.commit()


def _create_va_type():
    # only create va type when there are none
    va_type = VaType.query.count()
    if va_type == 0:
        # REGISTER VA TYPE HERE
        va_credit = VaType(key="CREDIT")
        # debit
        va_debit = VaType(key="DEBIT")
        db.session.add(va_debit)
        db.session.add(va_credit)
        db.session.commit()


def _create_transaction_type():
    transaction_types = TransactionType.query.all()
    # if there's nothing in the db we load everything
    if not transaction_types:
        datas = read_file("data/transaction_types.csv")
        for data in datas:
            transaction_type = TransactionType(key=data[0], description=data[1])
            db.session.add(transaction_type)
            db.session.commit()
    # if already some data we update or add new entry
    else:
        datas = read_file("data/transaction_types.csv")
        for data in datas:
            transaction_type = TransactionType.query.filter_by(key=data[0]).first()
            if transaction_type is None:
                transaction_type = TransactionType(key=data[0], description=data[1])
                db.session.add(transaction_type)
                db.session.commit()
            else:
                transaction_type.key = data[0]
                transaction_type.description = data[1]
                db.session.commit()


def _create_transaction_note():
    transaction_notes = TransactionNote.query.all()
    # if there's nothing in the db we load everything
    if not transaction_notes:
        datas = read_file("data/transaction_notes.csv")
        for data in datas:
            transaction_note = TransactionNote(key=data[0], notes=data[1])
            db.session.add(transaction_note)
            db.session.commit()
    # if already some data we update or add new entry
    else:
        datas = read_file("data/transaction_notes.csv")
        for data in datas:
            transaction_note = TransactionNote.query.filter_by(key=data[0]).first()
            if transaction_note is None:
                transaction_note = TransactionNote(key=data[0], notes=data[1])
                db.session.add(transaction_note)
                db.session.commit()
            else:
                transaction_note.key = data[0]
                transaction_note.notes = data[1]
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
            bank_id=bni.id,
        )
        db.session.add(payment_channel)
        db.session.commit()


def _create_api_key():
    # only create api key if there are none
    api_key = ApiKey.query.count()
    if api_key == 0:
        api_key = ApiKey(id="8c574c41-3e01-4763-89af-fd370989da33", name="modana_dev")
        db.session.add(api_key)
        db.session.commit()


def _create_quota():
    QuotaTask().generate_monthly_quota()


if __name__ == "__main__":
    manager.run()
