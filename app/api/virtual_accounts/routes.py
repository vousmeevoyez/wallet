"""
    Virtual-Accounts Routes
    _______________
"""
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods
# pylint: disable=no-name-in-module

from app.lib.core import Routes

from app.api.virtual_accounts import api

# serializer
from app.api.serializer import *

# request schema
from app.api.request_schema import *

# wallet modules
from app.api.virtual_accounts.modules.va_services import VirtualAccountServices

# authentication
from app.api.auth.decorator import admin_required

# exceptions
from app.api.utility.utils import UtilityError


@api.route("/")
class VirtualAccountRoutes(Routes):
    """
        virtualaccounts
        /virtual-accounts/
    """

    @admin_required
    def get(self):
        """ endpoint for getting all virtual accounts """
        response = VirtualAccountServices().show()
        return response

    # end def


@api.route("/<string:account_no>")
class VirtualAccountInfoRoutes(Routes):
    """
        Virtual Accounts
        /virtual-accounts/<account_no>
    """

    __schema__ = VirtualAccountUpdateRequestSchema
    __serializer__ = VirtualAccountSchema(strict=True)

    @admin_required
    def get(self, account_no):
        """ endpoint for getting singel virtual account """
        response = VirtualAccountServices(account_no).info()
        return response

    # end def

    @admin_required
    def put(self, account_no):
        """ endpoint for updating virtual account """
        request_data = self.serialize(self.payload())
        response = VirtualAccountServices(account_no).update(request_data)
        return response

    # end def

    @admin_required
    def delete(self, account_no):
        """ endpoint for deactivating virtual accounts  """
        response = VirtualAccountServices(account_no).remove()
        return response

    # end def


# end class


@api.route("/<string:account_no>/logs/")
class VirtualAccountLogsRoutes(Routes):
    """
        Virtual Accounts Logs
        /<account_no>/logs
    """

    @admin_required
    def get(self, account_no):
        """ endpoint for getting virtual accounts logs """
        response = VirtualAccountServices(account_no).get_logs()
        return response

    # end def
