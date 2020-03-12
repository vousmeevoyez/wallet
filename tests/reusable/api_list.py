"""
    API CALL LIST
"""
import json

BASE_URL = "/api/v1"


def dict_to_url_query(params):
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
        # end if
        counter += 1
    # end for
    return query


""" AUTHENTICATION """


def get_access_token(client, username, password):
    """ api call to get access token """
    return client.post(
        BASE_URL + "/auth/" + "token", data=dict(username=username, password=password)
    )


# end def
def get_refresh_token(client, refresh_token):
    """ api call to refresh token """
    headers = {"Authorization": "Bearer {}".format(refresh_token)}
    return client.post(BASE_URL + "/auth/" + "refresh", headers=headers)


# end def


def revoke_token(client, token):
    """ api call to revoke access token"""
    headers = {"Authorization": "Bearer {}".format(token)}
    return client.post(BASE_URL + "/auth/" + "token/revoke", headers=headers)


# end def

""" CALLBACK """


def withdraw_callback(client, params):
    """ api callback to withdraw """
    return client.post(
        BASE_URL + "/callback/bni/va/withdraw",
        data=json.dumps(params),
        content_type="application/json",
    )


# end def


def deposit_callback(client, params):
    """ api callback to deposit """
    return client.post(
        BASE_URL + "/callback/bni/va/deposit",
        data=json.dumps(params),
        content_type="application/json",
    )


# end def

""" USER """


def create_user(client, params, access_token):
    """ Create user """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(BASE_URL + "/users/", data=dict(**params), headers=headers)


# end def


def update_user(client, params, user_id, access_token):
    """ update user """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.put(
        BASE_URL + "/users/" + str(user_id),
        data=dict(
            name=params["name"],
            phone_ext=params["phone_ext"],
            phone_number=params["phone_number"],
            email=params["email"],
            password=params["password"],
        ),
        headers=headers,
    )


# end def


def get_all_user(client, access_token):
    """ get all user """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/users/", headers=headers)


# end def


def get_user(client, user_id, access_token):
    """ get user """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/users/" + user_id, headers=headers)


# end def

""" USER BANK ACCOUNT """


def create_user_bank_account(client, user_id, params, access_token):
    """ add userbank account """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/users/" + user_id + "/bank_account/",
        data=dict(
            account_no=params["account_no"],
            label=params["label"],
            name=params["name"],
            bank_id=params["bank_id"],
        ),
        headers=headers,
    )


# end def


def get_bank_account(client, user_id, access_token):
    """ get user """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(
        BASE_URL + "/users/" + user_id + "/bank_account/", headers=headers
    )


# end def


def remove_bank_account(client, user_id, bank_account_id, access_token):
    """ remove user bank account"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.delete(
        BASE_URL + "/users/" + user_id + "/bank_account/" + bank_account_id,
        headers=headers,
    )


# end def


def update_bank_account(client, user_id, bank_account_id, params, access_token):
    """ update userbank account """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.put(
        BASE_URL + "/users/" + user_id + "/bank_account/" + bank_account_id,
        data=dict(
            account_no=params["account_no"],
            label=params["label"],
            name=params["name"],
            bank_id=params["bank_id"],
        ),
        headers=headers,
    )


# end def

""" WALLET """


def create_wallet(client, params, access_token):
    """ Api Call for Creating Wallet """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/wallets/",
        data=dict(label=params["label"], pin=params["pin"]),
        headers=headers,
    )


# end def


def get_wallet_info(client, wallet_id, access_token):
    """ Api Call for getting wallet info"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/wallets/" + wallet_id, headers=headers)


# end def


def get_all_wallet(client, access_token):
    """ Api Call for show all wallet that user have"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/wallets/", headers=headers)


# end def


def remove_wallet(client, wallet_id, access_token):
    """ Remove Wallet """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.delete(BASE_URL + "/wallets/" + wallet_id, headers=headers)


# end def


def get_balance(client, wallet_id, access_token):
    """ Api Call for getting balance """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/wallets/" + wallet_id + "/balance/", headers=headers)


# end def


def get_transaction(client, wallet_id, params, access_token):
    """ Api Call for getting wallet transaction """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(
        BASE_URL
        + "/wallets/"
        + wallet_id
        + "/transactions?flag={}&start_date={}&end_date={}".format(
            params["flag"], params["start_date"], params["end_date"]
        ),
        headers=headers,
    )


# end def


def get_transaction_details(client, wallet_id, params, access_token):
    """ Api Call for getting wallet transaction details """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(
        BASE_URL
        + "/wallets/"
        + wallet_id
        + "/transactions/{}".format(params["transaction_id"]),
        headers=headers,
    )


# end def


def check_pin(client, wallet_id, params, access_token):
    """ Api Call for checking pin """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/wallets/" + wallet_id + "/pin/",
        data=dict(pin=params["pin"]),
        headers=headers,
    )


# end def


def update_pin(client, wallet_id, params, access_token):
    """ Api Call for updating pin """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.put(
        BASE_URL + "/wallets/" + wallet_id + "/pin/",
        data=dict(
            old_pin=params["old_pin"],
            pin=params["pin"],
            confirm_pin=params["confirm_pin"],
        ),
        headers=headers,
    )


# end def


def transfer(client, source, destination, params, access_token):
    """ Api Call for transfer between wallet """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/wallets/" + "{}/transfer/{}".format(source, destination),
        data=dict(
            amount=params["amount"],
            pin=params["pin"],
            notes=params["notes"],
            types=params["types"],
        ),
        headers=headers,
    )


# end def


def bank_transfer(client, source, destination, params, access_token):
    """ Api Call for transfer between wallet """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/wallets/" + "{}/transfer/bank/{}".format(source, destination),
        data=dict(amount=params["amount"], pin=params["pin"], notes=params["notes"]),
        headers=headers,
    )


# end def


def bank_transfer2(client, source, destination, params, api_key):
    """ Api Call for transfer between wallet """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.post(
        BASE_URL + "/wallets/" + "{}/transfer/bank2/{}".format(source, destination),
        data=dict(amount=params["amount"], pin=params["pin"], notes=params["notes"]),
        headers=headers,
    )


# end def


def forgot_pin(client, source, access_token):
    """ Api Call for forgot wallet pin"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(
        BASE_URL + "/wallets/" + "{}/forgot/".format(source), headers=headers
    )


# end def


def verify_forgot_pin(client, source, params, access_token):
    """ Api Call for verify forgot wallet pin"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/wallets/" + "{}/forgot/".format(source),
        data=dict(
            otp_key=params["otp_key"], otp_code=params["otp_code"], pin=params["pin"]
        ),
        headers=headers,
    )


# end def


def withdraw(client, source, params, access_token):
    """ Api Call for withdraw wallet """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/wallets/" + "{}/withdraw/".format(source),
        data=dict(amount=params["amount"], pin=params["pin"]),
        headers=headers,
    )


# end def


def get_qr(client, wallet_id, access_token):
    """ Api Call for getting qr string """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/wallets/" + wallet_id + "/qr/", headers=headers)


# end def


def qr_checkout(client, wallet_id, params, access_token):
    """ Api Call for getting qr string checkout """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/wallets/" + wallet_id + "/qr/checkout",
        data=dict(qr_string=params["qr_string"]),
        headers=headers,
    )


# end def


def refund_transaction(client, transaction_id, access_token):
    """ Api Call for refunding transaction """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.delete(
        BASE_URL + "/transactions/refund/" + transaction_id, headers=headers
    )


# end def

"""
    PAYMENT PLAN 
"""


def create_payment_plan(client, params, api_key):
    """ Api Call for creating payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.post(
        BASE_URL + "/payment_plans/",
        data=json.dumps(params),
        content_type="application/json",
        headers=headers,
    )


# end def


def get_payment_plan(client, payment_plan_id, api_key):
    """ Api Call for getting payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.get(BASE_URL + "/payment_plans/" + payment_plan_id, headers=headers)


# end def


def get_payment_plans(client, api_key):
    """ Api Call for getting all payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.get(BASE_URL + "/payment_plans/", headers=headers)


# end def


def update_payment_plan(client, payment_plan_id, params, api_key):
    """ Api Call for update payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.put(
        BASE_URL + "/payment_plans/" + payment_plan_id,
        data=dict(destination=params["destination"], wallet_id=params["wallet_id"]),
        headers=headers,
    )


# end def


def remove_payment_plan(client, payment_plan_id, api_key):
    """ Api Call for remove payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.delete(
        BASE_URL + "/payment_plans/" + payment_plan_id, headers=headers
    )


# end def

"""
    PLAN 
"""


def create_plan(client, params, api_key):
    """ Api Call for creating plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.post(
        BASE_URL + "/plans/",
        data=json.dumps(params),
        content_type="application/json",
        headers=headers,
    )


# end def


def get_plan(client, plan_id, api_key):
    """ Api Call for getting payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.get(BASE_URL + "/plans/" + plan_id, headers=headers)


# end def


def get_plans(client, api_key):
    """ Api Call for getting all payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.get(BASE_URL + "/plans/", headers=headers)


# end def


def update_plan(client, plan_id, params, api_key):
    """ Api Call for update payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.put(
        BASE_URL + "/plans/" + plan_id,
        data=json.dumps(params),
        content_type="application/json",
        headers=headers,
    )


# end def


def update_plan_status(client, plan_id, params, api_key):
    """ Api Call for update payment plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.patch(
        BASE_URL + "/plans/" + plan_id,
        data=json.dumps(params),
        content_type="application/json",
        headers=headers,
    )


# end def


def remove_plan(client, plan_id, api_key):
    """ Api Call for remove plan """
    headers = {"X-Api-Key": "{}".format(api_key)}
    return client.delete(BASE_URL + "/plans/" + plan_id, headers=headers)


# end def

# end def


def health_check(client):
    """ Api Call for checking services health """
    return client.get(BASE_URL + "/utility/health")


# end def

""" BANKS """


def get_all_banks(client):
    """ api call to get all bank stored """
    return client.get(BASE_URL + "/banks/")


def check_bni_balance(client, account_no, access_token):
    """ Api Call for getting bni account balance """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/banks/bni/balance/" + account_no, headers=headers)


# end def


def check_bni_inquiry(client, account_no, access_token):
    """ Api Call for getting bni account information """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/banks/bni/inquiry/" + account_no, headers=headers)


# end def


def check_bni_payment(client, reference_number, access_token):
    """ Api Call for getting bni reference number"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(
        BASE_URL + "/banks/bni/payment/" + reference_number, headers=headers
    )


# end def


def void_bni_payment(client, params, access_token):
    """ Api Call for cancelling bni transfer"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.delete(
        BASE_URL + "/banks/bni/payment/" + params["reference_number"],
        data=dict(account_no=params["account_no"], amount=params["amount"]),
        headers=headers,
    )


# end def


def bni_do_payment(client, params, access_token):
    """ Api Call for do payment """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(BASE_URL + "/banks/bni/payment/", data=params, headers=headers)


def bni_interbank_inquiry(client, params, access_token):
    """ Api Call for do bni interbank inquiry"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    # build argument query
    query = dict_to_url_query(params)
    return client.get(
        BASE_URL + "/banks/bni/interbank/payment/{}".format(query), headers=headers
    )


def bni_interbank_payment(client, params, access_token):
    """ Api Call for do bni interbank payment"""
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.post(
        BASE_URL + "/banks/bni/interbank/payment/", data=params, headers=headers
    )


"""
    Virtual Accounts
"""


def get_virtual_accounts(client, access_token):
    """ Api Call for gettign all virtual accounts """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(BASE_URL + "/virtual_accounts/", headers=headers)


def get_virtual_account(client, account_no, access_token):
    """ Api Call for gettign virtual account """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(
        BASE_URL + "/virtual_accounts/{}".format(account_no), headers=headers
    )


def get_virtual_account_logs(client, account_no, access_token):
    """ Api Call for gettign logs for virtual account """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.get(
        BASE_URL + "/virtual_accounts/{}/logs/".format(account_no), headers=headers
    )


def update_virtual_account(client, access_token, account_no, params):
    """ Api Call for gettign updating virtual accounts """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.put(
        BASE_URL + "/virtual_accounts/{}".format(account_no),
        headers=headers,
        data=params,
    )


def remove_virtual_account(client, access_token, account_no):
    """ Api Call for gettign removing /deactivating virtual accounts """
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return client.delete(
        BASE_URL + "/virtual_accounts/{}".format(account_no),
        headers=headers
    )
