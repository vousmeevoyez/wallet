"""
    Wallet Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods

from flask_restplus     import Resource
from marshmallow import ValidationError

from app.api.wallet import api
#serializer
from app.api.serializer import *
# request schema
from app.api.request_schema import *

# wallet modules
from app.api.wallet.modules.wallet_services import WalletServices
from app.api.wallet.modules.transfer_services import TransferServices
from app.api.wallet.modules.withdraw_services import WithdrawServices

# authentication
from app.api.authentication.decorator import token_required
from app.api.authentication.decorator import get_token_payload
from app.api.authentication.decorator import admin_required

from app.api.common.helper import QR
from app.api.common.modules.cipher import DecryptError

# exceptions
from app.api.error.http import *
# configuration
from app.config import config

ERROR_CONFIG = config.Config.ERROR_CONFIG

# REQUEST SCHEMA HERE
wallet_request_schema = WalletRequestSchema.parser
update_pin_request_schema = WalletUpdatePinRequestSchema.parser
forgot_pin_request_schema = ForgotPinRequestSchema.parser
transfer_request_schema = TransferRequestSchema.parser
wallet_transaction_request_schema = WalletTransactionRequestSchema.parser
qr_transfer_request_schema = QRTransferRequestSchema.parser
withdraw_request_schema = WithdrawRequestSchema.parser

@api.route('/')
class WalletAddRoutes(Resource):
    """
        Wallet add Routes
        api/v1/wallet/<user_id>
    """
    @token_required
    def post(self):
        """
            Handle POST request from
            api/v1/wallet/<user_id>
        """
        payload = get_token_payload()
        user = payload["user"]

        request_data = wallet_request_schema.parse_args(strict=True)
        try:
            wallet = WalletSchema(strict=True).load(request_data)
        except ValidationError as error:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)

        response = WalletServices.add(user, wallet.data, request_data["pin"])
        return response
    #end def

    @token_required
    def get(self):
        """
            Handle GET request from
            api/v1/wallet/<user_id>
        """
        payload = get_token_payload()
        user = payload["user"]

        response = WalletServices.show(user)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>')
class WalletRoutes(Resource):
    """
        Wallet Routes
        api/v1/wallet/
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/wallet/
            return wallet information
        """
        response = WalletServices(wallet_id).info()
        return response
    #end def

    def delete(self, wallet_id):
        """
            handle DELETE method from
            api/v1/wallet/
        """
        response = WalletServices(wallet_id).remove()
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/qr/')
class WalletQrRoutes(Resource):
    """
        Wallet QR Routes
        api/v1/<wallet_id>/qr
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/qr
            return wallet qr
        """
        response = WalletServices(wallet_id).get_qr()
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/qr/transfer')
class WalletQrTransferRoutes(Resource):
    """
        Wallet QR Routes
        api/v1/<wallet_id>/qr
    """
    @token_required
    def post(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/qr
            return wallet qr
        """
        # request data validator
        request_data = qr_transfer_request_schema.parse_args(strict=True)
        try:
            transfer = TransactionSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if
        # Decrypt QR Code here
        try:
            payload = QR().read(request_data["qr_string"])
            destination = payload["wallet_id"]
        except DecryptError:
            raise BadRequest(ERROR_CONFIG["INVALID_QR"]["TITLE"],
                             ERROR_CONFIG["INVALID_QR"]["MESSAGE"])
        #end try
        response = TransferServices(wallet_id,
                                    request_data["pin"],
                                    destination).internal_transfer(request_data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/balance/')
class WalletBalanceRoutes(Resource):
    """
        Wallet Balance Routes
        api/v1/<wallet_id>/balance
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/balance
            return wallet balance
        """
        response = WalletServices(wallet_id).check_balance()
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/transactions')
class WalletTransactionRoutes(Resource):
    """
        Wallet Transaction Routes
        api/v1/<wallet_id>/transactions
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/transactions
            return wallet transaction list
        """
        request_data = wallet_transaction_request_schema.parse_args(strict=True)
        try:
            wallet = WalletTransactionSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)

        response = WalletServices(wallet_id).history(request_data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/transactions/<transaction_id>')
class WalletTransactionDetailsRoutes(Resource):
    """
        Wallet Transaction Details Routes
        api/v1/<wallet_id>/transactions/<transaction_id>
    """
    @token_required
    def get(self, wallet_id, transaction_id):
        """
            handle GET method from
            api/v1/<wallet_id>/transactions/<transaction_id>
            return wallet transaction details
        """
        response = WalletServices(wallet_id).history_details(transaction_id)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/pin/')
class WalletPinRoutes(Resource):
    """
        Wallet pin routes
        api/v1/<wallet_id>/pin/
    """
    @token_required
    def put(self, wallet_id):
        """
            handle Put method from
            api/v1/<wallet_id>/pin/
            update wallet pin
        """
        request_data = update_pin_request_schema.parse_args(strict=True)
        # need to serialize here
        response = WalletServices(wallet_id).update_pin(request_data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/forgot/')
class WalletForgotPinRoutes(Resource):
    """
        Wallet Forgot Pin ROutes
        api/v1/<wallet_id>/forgot/
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/forgot/
            send forgot pin otp via sms
        """
        response = WalletServices(wallet_id).send_forgot_otp()
        return response
    #end def

    @token_required
    def post(self, wallet_id):
        """
            handle POST method from
            api/v1/<wallet_id>/forgot/
            verify forgot pin
        """
        request_data = forgot_pin_request_schema.parse_args(strict=True)
        # need to serialize here
        response = WalletServices(wallet_id).verify_forgot_otp(request_data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/withdraw/')
class WalletWithdrawRoutes(Resource):
    """
        Wallet Withdraw Routes
        api/v1/<wallet_id>/withdraw/
    """
    @token_required
    def post(self, wallet_id):
        """
            handle POST method from
            api/v1/<wallet_id>/withdraw/
            withdraw money
        """
        request_data = withdraw_request_schema.parse_args(strict=True)
        try:
            result = WithdrawSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end try

        # need to serialize here
        request_data["bank_name"] = "BNI"
        response = WithdrawServices(wallet_id,
                                    request_data["pin"]).request(request_data)
        return response
    #end def
#end class

@api.route('/<int:source_wallet_id>/transfer/<int:destination_wallet_id>')
class WalletTransferRoutes(Resource):
    """
        Wallet Transfer Routes
        api/v1/<source>/transfer/<destination>
    """
    @token_required
    def post(self, source_wallet_id, destination_wallet_id):
        """
            handle POST method from
            api/v1/<source>/transfer/<destination>
            send money between VA
        """
        # parse request data
        request_data = transfer_request_schema.parse_args(strict=True)
        try:
            transfer = TransactionSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if
        response = TransferServices(source_wallet_id,
                                    request_data["pin"],
                                    destination_wallet_id).internal_transfer(request_data)
        return response
    #end def
#end class

@api.route('/<int:source_wallet_id>/transfer/bank/<int:bank_account_id>')
class WalletBankTransferRoutes(Resource):
    """
        Wallet Bank Transfer Routes
        api/v1/source/transfer/bank/<bank_account_id>
    """
    @token_required
    def post(self, source_wallet_id, bank_account_id):
        """
            handle POST method from
            api/v1/<source>/transfer/bank/<bank_account_id>
            send money to bank account
        """
        # parse request data
        request_data = transfer_request_schema.parse_args(strict=True)
        try:
            transfer = TransactionSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if

        request_data["destination"] = bank_account_id
        response = TransferServices(source_wallet_id,
                                    request_data["pin"]).external_transfer(request_data)
        return response
    #end def
#end class
