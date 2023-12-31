"""
    User Services
    _______________
"""
# pylint: disable=no-name-in-module
# pylint: disable=import-error
from sqlalchemy.exc import IntegrityError

# database
from app.api import db

# models
from app.api.models import User, Wallet

# serializer
from app.api.serializer import UserSchema

# services
from app.api.wallets.modules.wallet_services import WalletServices

# http response
from app.lib.http_response import ok, created, no_content

# utility
from app.api.utility.utils import validate_uuid

# exceptions
from app.lib.http_error import RequestNotFound, UnprocessableEntity

# const
from app.api.const import STATUS

# configuration
from app.api.const import ERROR as error_response


class UserServices:
    """ User Services Class"""

    def __init__(self, user_id=None):
        if user_id is not None:
            # look up user only if user_id is set
            user = User.query.filter_by(
                id=validate_uuid(user_id), status=STATUS["ACTIVE"]
            ).first()
            if user is None:
                raise RequestNotFound(
                    error_response["USER_NOT_FOUND"]["TITLE"],
                    error_response["USER_NOT_FOUND"]["MESSAGE"],
                )
            # end if
            self.user = user

    # end def

    def add(self, user, password, pin, label):
        """
            add new user
            create wallet
            create virtual account
        """
        try:
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
        except IntegrityError as error:
            # print(err.orig)
            db.session.rollback()
            raise UnprocessableEntity(
                error_response["DUPLICATE_USER"]["TITLE"],
                error_response["DUPLICATE_USER"]["MESSAGE"],
            )
        # end try

        # create wallet object first
        try:
            wallet = Wallet(label=label)
            result = WalletServices().add(user, wallet, pin)
        except UnprocessableEntity as error:
            pass

        wallet_id = result[0]["data"]["wallet_id"]

        response = {"user_id": str(user.id), "wallet_id": wallet_id}
        return created(response)

    # end def

    def show(self, page):
        """ show all stored user for admin"""
        users = User.query.filter_by(status=STATUS["ACTIVE"]).all()
        response = UserSchema(many=True).dump(users).data
        return ok(response)

    # end def

    def info(self):
        """ return single user information"""
        user_information = UserSchema().dump(self.user).data
        return ok(user_information)

    # end def

    def update(self, params):
        """ update user information """
        self.user.name = params["name"]
        self.user.phone_ext = params["phone_ext"]

        # checking each fields and make sure its not the same as the old one
        # and must be unique
        error = []
        phone_number = params["phone_number"]
        if self.user.phone_number == phone_number:
            error.append(
                {"phone_number": ["Phone number can't be the same with the old one"]}
            )

        email = params["email"]
        if email is not None:
            if self.user.email == email:
                error.append({"email": ["email can't be the same with the old one"]})

        if error != []:
            raise UnprocessableEntity(
                error_response["DUPLICATE_UPDATE_ENTRY"]["TITLE"],
                error_response["DUPLICATE_UPDATE_ENTRY"]["MESSAGE"],
                error,
            )

        self.user.set_password(params["password"])
        self.user.email = email
        self.user.phone_number = phone_number

        db.session.commit()
        return no_content()

    # end def

    def remove(self):
        """ remove user, just deactivate their account """
        try:
            # self.user.status = STATUS_CONFIG["DEACTIVE"]
            db.session.delete(self.user)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
        # end try
        return no_content()

    # end def


# end class
