"""
    Test User Routes
"""
import json

from tests.reusable.api_list import *


"""
    TEST BEGIN HERE 
"""

def test_create_user_routes_success(client, setup_admin_token):
    """ test routes function to create user"""
    params = {
        "username": "jennie",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219643444",
        "email": "jennie@blackpink.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    result = create_user(client, params, setup_admin_token)
    response = result.get_json()["data"]

    assert response["user_id"]

def test_create_user_routes_failed_validate_input(client, setup_admin_token):
    """ test routes function to create user but there are some invalid data
    passed to this routes"""
    params = {
        "username": "",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81219643444",
        "email": "jennie@blackpink.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    result = create_user(client, params, setup_admin_token)
    assert result.status_code == 400  # bad request

def test_get_all_user(client, setup_admin_token):
    """ test method that return all user """
    result = get_all_user(client, setup_admin_token)
    status_code = result.status_code

    assert status_code == 200  # ok

def test_update_user(client, setup_admin_token):
    """ test routes function to update user"""
    params = {
        "username": "roserose",
        "name": "roserose",
        "phone_ext": "62",
        "phone_number": "91219643444",
        "email": "rose@blackpink.com",
        "password": "password",
        "pin": "123456",
        "role": "USER",
        "label": "PERSONAL",
    }
    result = create_user(client, params, setup_admin_token)
    response = result.get_json()["data"]

    user_id = response["user_id"]

    params = {
        "name": "jennai",
        "phone_ext": "62",
        "phone_number": "81219644444",
        "email": "jennie@blckpink.com",
        "password": "password",
    }
    result = update_user(client, params, user_id, setup_admin_token)
    assert result.status_code == 204

def test_get_user(client, setup_user_wallet_va, setup_admin_token):
    """ test method that get user info"""
    access_token, user_id, wallet_id = setup_user_wallet_va

    result = get_user(client, user_id, access_token)
    assert result.status_code == 200  # ok

def test_create_user_bank_account_success(client, setup_user_wallet_va):
    """ test method that get user info"""
    # get access token first
    access_token, user_id, wallet_id = setup_user_wallet_va

    params = {
        "account_no": "3333333333",
        "name": "Bpk KEN AROK",
        "label": "Irene Bank Account",
        "bank_code": "014",
    }

    result = create_user_bank_account(client, user_id, params, access_token)
    assert result.status_code == 201  # created

def test_create_user_bank_account_validate_failed(client, setup_user_wallet_va):
    """ test method that get user info but failed because some invalid
    input"""

    access_token, user_id, wallet_id = setup_user_wallet_va

    params = {
        "account_no": "",
        "name": "Bpk KEN AROK",
        "label": "Irene Bank Account",
        "bank_code": "014",
    }

    result = create_user_bank_account(client, user_id, params, access_token)
    assert result.status_code == 400  # ok

    params = {
        "account_no": "123132123132131",
        "name": "aaaaaaaaaaaaaa aaaaaaaaaa aaaaaaaaaaaa\
        aaaaaaaaaaaaaaaaaaaaaaaaaa",
        "label": "Irene Bank Account",
        "bank_code": "014",
    }

    result = create_user_bank_account(client, user_id, params, access_token)
    assert result.status_code == 400  # ok

def test_get_user_bank_account(client, setup_user_wallet_va):
    """ test routes that return bank account information"""
    access_token, user_id, wallet_id = setup_user_wallet_va

    result = get_bank_account(client, user_id, access_token)
    assert result.status_code == 200  # ok

def test_update_user_bank_account_success(client, setup_user_wallet_va):
    """ test method that update user bank account information"""
    access_token, user_id, wallet_id = setup_user_wallet_va

    params = {
        "account_no": "3333333333",
        "name": "Bpk KEN AROK",
        "label": "Irene Bank Account",
        "bank_code": "014",
    }

    result = create_user_bank_account(client, user_id, params, access_token)
    assert result.status_code == 201  # ok

    bank_account_id = result.get_json()["data"]["bank_account_id"]

    # get access token first
    params = {
        "account_no": "1111333333",
        "name": "Bpk KEN AROK",
        "label": "Kelvin Bank Accounts",
        "bank_code": "014",
    }
    result = update_bank_account(
        client, user_id, bank_account_id, params, access_token
    )
    status_code = result.status_code

    assert status_code == 204  # ok

def test_remove_bank_account(client, setup_user_wallet_va):
    """ test method that remove user bank account information"""
    access_token, user_id, wallet_id = setup_user_wallet_va

    params = {
        "account_no": "3333333333",
        "name": "Bpk KEN AROK",
        "label": "Irene Bank Account",
        "bank_code": "014",
    }

    result = create_user_bank_account(client, user_id, params, access_token)
    assert result.status_code == 201  # ok

    bank_account_id = result.get_json()["data"]["bank_account_id"]

    # get access token first
    params = {
        "account_no": "1111333333",
        "name": "Bpk KEN AROK",
        "label": "Kelvin Bank Accounts",
        "bank_code": "014",
    }
    result = remove_bank_account(
        client, user_id, bank_account_id, access_token
    )
    status_code = result.status_code

    assert status_code == 204  # ok
