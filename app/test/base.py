from os import path
import json
import csv

from flask_testing  import TestCase
from unittest.mock import Mock, patch

from manage         import app, init
from app.api        import db
# configuration
from app.config import config
# models
from app.api.models import User
from app.api.models import Role
from app.api.models import VaType
from app.api.models import PaymentChannel
from app.api.models import Bank

TEST_CONFIG = config.TestingConfig
BASE_URL = "/api/v1"

class BaseTestCase(TestCase):
    """ This is Base Tests """

    user = None

    def create_app(self):
        """ create flask app in test mode"""
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

        username = "somerandomstranger"
        user = User.query.filter_by(username=username).first()
        if user is None:
            # add dummy user
            user = User(
                username=username,
                name='somerandomstranger',
                email='somerandomstranger@test.com',
                phone_ext='62',
                phone_number='88308644314',
                role_id=role.id,
            )
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

        self.user = user

    def _dict_to_url_query(self, params):
        # pattern ?key=value
        query = ""
        pattern = "{}={}"
        counter = 1
        for key, value in params.items():
            query = query + pattern.format(key, value)
            if counter == 1:
                query = "?" + query

            if counter != len(params):
                query = query + "&"
            #end if
            counter += 1
        #end for
        return query

    """
        API CALL
    """
    """ AUTHENTICATION """
    def get_access_token(self, username, password):
        """ api call to get access token """
        return self.client.post(
            BASE_URL + "/auth/" + "token",
            data=dict(
                username=username,
                password=password
            )
        )
    #end def
    def get_refresh_token(self, refresh_token):
        """ api call to refresh token """
        headers = {
            'Authorization': 'Bearer {}'.format(refresh_token)
        }
        return self.client.post(
            BASE_URL + "/auth/" + "refresh",
            headers=headers
        )
    #end def

    def revoke_access_token(self, access_token):
        """ api call to revoke access token"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/auth/" + "token/revoke",
            headers=headers
        )
    #end def

    def revoke_refresh_token(self, refresh_token):
        """ api call to revoke refresh token """
        headers = {
            'Authorization': 'Bearer {}'.format(refresh_token)
        }
        return self.client.post(
            BASE_URL + "/auth/" + "refresh/revoke",
            headers=headers
        )
        #end def

    """ CALLBACK """
    def withdraw_callback(self, params):
        """ api callback to withdraw """
        return self.client.post(
            BASE_URL + "/callback/bni/va/withdraw",
            data=json.dumps(params),
            content_type="application/json"
        )
    #end def

    def deposit_callback(self, params):
        """ api callback to deposit """
        return self.client.post(
            BASE_URL + "/callback/bni/va/deposit",
            data=json.dumps(params),
            content_type="application/json"
        )
    #end def

    """ USER """
    def create_user(self, params, access_token):
        """ Create user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/users/",
            data=dict(
                username=params["username"],
                name=params["name"],
                phone_ext=params["phone_ext"],
                phone_number=params["phone_number"],
                email=params["email"],
                password=params["password"],
                pin=params["pin"],
                role=params["role"]
            ),
            headers=headers
        )
    #end def

    def update_user(self, params, user_id, access_token):
        """ update user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.put(
            BASE_URL + "/users/"+ str(user_id),
            data=dict(
                name=params["name"],
                phone_ext=params["phone_ext"],
                phone_number=params["phone_number"],
                email=params["email"],
                password=params["password"],
            ),
            headers=headers
        )
    #end def

    def get_all_user(self, access_token):
        """ get all user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/users/",
            headers=headers
        )
    #end def

    def get_user(self, user_id, access_token):
        """ get user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/users/" + user_id,
            headers=headers
        )
    #end def

    """ USER BANK ACCOUNT """
    def create_user_bank_account(self, user_id, params, access_token):
        """ add userbank account """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/users/" + user_id + "/bank_account/",
            data=dict(
                account_no=params["account_no"],
                label=params["label"],
                name=params["name"],
                bank_code=params["bank_code"]
            ),
            headers=headers
        )
    #end def

    def get_bank_account(self, user_id, access_token):
        """ get user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/users/" + user_id + "/bank_account/",
            headers=headers
        )
    #end def

    def remove_bank_account(self, user_id, bank_account_id, access_token):
        """ remove user bank account"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.delete(
            BASE_URL + "/users/" + user_id + "/bank_account/" + bank_account_id,
            headers=headers
        )
    #end def

    def update_bank_account(self, user_id, bank_account_id, params, access_token):
        """ update userbank account """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.put(
            BASE_URL + "/users/" + user_id + "/bank_account/" + bank_account_id,
            data=dict(
                account_no=params["account_no"],
                label=params["label"],
                name=params["name"],
                bank_code=params["bank_code"]
            ),
            headers=headers
        )
    #end def

    """ WALLET """
    def create_wallet(self, params, access_token):
        """ Api Call for Creating Wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/wallets/",
            data=dict(
                label=params["label"],
                pin=params["pin"]
            ),
            headers=headers
        )
    #end def

    def get_wallet_info(self, wallet_id, access_token):
        """ Api Call for getting wallet info"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/wallets/" + wallet_id,
            headers=headers
        )
    #end def

    def get_all_wallet(self, access_token):
        """ Api Call for show all wallet that user have"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/wallets/",
            headers=headers
        )
    #end def

    def remove_wallet(self, wallet_id, access_token):
        """ Remove Wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.delete(
            BASE_URL + "/wallets/" + wallet_id,
            headers=headers
        )
    #end def

    def get_balance(self, wallet_id, access_token):
        """ Api Call for getting balance """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/wallets/" + wallet_id + "/balance/",
            headers=headers
        )
    #end def

    def get_transaction(self, wallet_id, params, access_token):
        """ Api Call for getting wallet transaction """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/wallets/" + wallet_id +
            "/transactions?flag={}&start_date={}&end_date={}".format(params["flag"],
                                                                     params["start_date"],
                                                                     params["end_date"]),
            headers=headers
        )
    #end def

    def get_transaction_details(self, wallet_id, params, access_token):
        """ Api Call for getting wallet transaction details """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/wallets/" + wallet_id +
            "/transactions/{}".format(params["transaction_id"]),
            headers=headers
        )
    #end def

    def check_pin(self, wallet_id, params, access_token):
        """ Api Call for checking pin """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/wallets/" + wallet_id + "/pin/",
            data=dict(
                pin=params["pin"],
            ),
            headers=headers
        )
    #end def

    def update_pin(self, wallet_id, params, access_token):
        """ Api Call for updating pin """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.put(
            BASE_URL + "/wallets/" + wallet_id + "/pin/",
            data=dict(
                old_pin=params["old_pin"],
                pin=params["pin"],
                confirm_pin=params["confirm_pin"]
            ),
            headers=headers
        )
    #end def

    def transfer(self, source, destination, params, access_token):
        """ Api Call for transfer between wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/wallets/" + "{}/transfer/{}".format(source, destination),
            data=dict(
                amount=params["amount"],
                pin=params["pin"],
                notes=params["notes"]
            ),
            headers=headers
        )
    #end def

    def bank_transfer(self, source, destination, params, access_token):
        """ Api Call for transfer between wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/wallets/" + "{}/transfer/bank/{}".format(source, destination),
            data=dict(
                amount=params["amount"],
                pin=params["pin"],
                notes=params["notes"]
            ),
            headers=headers
        )
    #end def

    def forgot_pin(self, source, access_token):
        """ Api Call for forgot wallet pin"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/wallets/" + "{}/forgot/".format(source),
            headers=headers
        )
    #end def

    def verify_forgot_pin(self, source, params, access_token):
        """ Api Call for verify forgot wallet pin"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/wallets/" + "{}/forgot/".format(source),
            data=dict(
                otp_key=params["otp_key"],
                otp_code=params["otp_code"],
                pin=params["pin"],
            ),
            headers=headers
        )
    #end def

    def withdraw(self, source, params, access_token):
        """ Api Call for withdraw wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/wallets/" + "{}/withdraw/".format(source),
            data=dict(
                amount=params["amount"],
                pin=params["pin"]
            ),
            headers=headers
        )
    #end def

    def get_qr(self, wallet_id, access_token):
        """ Api Call for getting qr string """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/wallets/" + wallet_id + "/qr/",
            headers=headers
        )
    #end def

    def qr_checkout(self, wallet_id, params, access_token):
        """ Api Call for getting qr string checkout """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/wallets/" + wallet_id + "/qr/checkout",
            data=dict(
                qr_string=params["qr_string"],
            ),
            headers=headers
        )
    #end def

    def refund_transaction(self, transaction_id, access_token):
        """ Api Call for refunding transaction """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.delete(
            BASE_URL + "/transactions/refund/" + transaction_id,
            headers=headers
        )
    #end def

    """
        PAYMENT PLAN 
    
    """
    def create_payment_plan(self, params, api_key):
        """ Api Call for creating payment plan """
        headers = {
            'X-Api-Key': 'Bearer {}'.format(api_key)
        }
        return self.client.post(
            BASE_URL + "/payment_plans/",
            data=json.dumps(params),
            content_type="application/json",
            headers=headers
        )
    #end def

    def get_payment_plan(self, payment_plan_id, api_key):
        """ Api Call for getting payment plan """
        headers = {
            'X-Api-Key': 'Bearer {}'.format(api_key)
        }
        return self.client.get(
            BASE_URL + "/payment_plans/" + payment_plan_id,
            headers=headers
        )
    #end def

    def get_payment_plans(self, api_key):
        """ Api Call for getting all payment plan """
        headers = {
            'X-Api-Key': 'Bearer {}'.format(api_key)
        }
        return self.client.get(
            BASE_URL + "/payment_plans/",
            headers=headers
        )
    #end def

    def update_payment_plan(self, payment_plan_id, params, api_key):
        """ Api Call for update payment plan """
        headers = {
            'X-Api-Key': 'Bearer {}'.format(api_key)
        }
        return self.client.put(
            BASE_URL + "/payment_plans/" + payment_plan_id,
            data=dict(
                destination=params["destination"],
                wallet_id=params["wallet_id"],
            ),
            headers=headers
        )
    #end def

    def remove_payment_plan(self, payment_plan_id, api_key):
        """ Api Call for remove payment plan """
        headers = {
            'X-Api-Key': 'Bearer {}'.format(api_key)
        }
        return self.client.delete(
            BASE_URL + "/payment_plans/" + payment_plan_id,
            headers=headers
        )
    #end def

    """
        BNI UTILITY
    """
    def check_bni_balance(self, account_no, access_token):
        """ Api Call for getting bni account balance """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/banks/bni/balance/" + account_no,
            headers=headers
        )
    #end def

    def check_bni_inquiry(self, account_no, access_token):
        """ Api Call for getting bni account information """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/banks/bni/inquiry/" + account_no,
            headers=headers
        )
    #end def

    def check_bni_payment(self, reference_number, access_token):
        """ Api Call for getting bni reference number"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + "/banks/bni/payment/" + reference_number,
            headers=headers
        )
    #end def

    def void_bni_payment(self, params, access_token):
        """ Api Call for cancelling bni transfer"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.delete(
            BASE_URL + "/banks/bni/payment/" + params["reference_number"],
            data=dict(
                account_no=params["account_no"],
                amount=params["amount"]
            ),
            headers=headers
        )
    #end def

    def bni_do_payment(self, params, access_token):
        """ Api Call for do payment """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/banks/bni/payment/",
            data=dict(
                method=params["method"],
                source_account=params["source_account"],
                account_no=params["account_no"],
                amount=params["amount"],
                email=params["email"],
                clearing_code=params["clearing_code"],
                account_name=params["account_name"],
                address=params["address"],
                charge_mode=params["charge_mode"],
            ),
            headers=headers
        )
    #end def

    def bni_interbank_inquiry(self, params, access_token):
        """ Api Call for do bni interbank inquiry"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        # build argument query
        query = self._dict_to_url_query(params)
        return self.client.get(
            BASE_URL + "/banks/bni/interbank/payment/{}".format(query),
            headers=headers
        )
    #end def

    def bni_interbank_payment(self, params, access_token):
        """ Api Call for do bni interbank payment"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/banks/bni/interbank/payment/",
            data=dict(
                source_account=params["source_account"],
                account_no=params["account_no"],
                account_name=params["account_name"],
                amount=params["amount"],
                bank_code=params["bank_code"],
                bank_name=params["bank_name"],
                transfer_ref=params["transfer_ref"]
            ),
            headers=headers
        )
    #end def
#end class
