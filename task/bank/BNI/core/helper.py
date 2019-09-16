"""
    BNI Bank Helper
    _________________
    this is module to interact with BNI Virtual Account &
    Core Banking API
"""
# pylint: disable=too-many-nested-blocks
# pylint: disable=redefined-outer-name
# pylint: disable=bad-whitespace
from functools import wraps

from datetime import datetime
import random

from werkzeug.contrib.cache import SimpleCache


from task.bank.BNI.core.request import BNIOpgAuthRequest
from task.bank.BNI.core.response import BNIOpgAuthResponse, ResponseError

from task.bank.lib.remote_call import RemoteCall, RemoteCallError

from task.bank.lib.exceptions import BaseError

# configuration
from app.config.external.bank import BNI_OPG


class CallError(BaseError):
    """ raised when call failed """


def generate_ref_number():
    """ generate reference number matched to BNI format"""
    now = datetime.utcnow()
    value_date = now.strftime("%Y%m%d%H%M%S")
    code = random.randint(1, 99999)
    return str(value_date) + str(code)


# end def


def generate_url(api_name, token=None):
    routes = BNI_OPG["ROUTES"]
    base_url = BNI_OPG["BASE_URL"] + ":" + BNI_OPG["PORT"]

    url = base_url + routes[api_name]
    if token is not None:
        url = url + "?access_token=" + token
    # end if
    return url


def call(request_contract, response_contract):
    """
        send request to BNI server and adjust everything
        according to BNI
        args :
            payload -- request payload
    """
    # assign client in in payload
    response = {}
    try:
        response["data"] = RemoteCall(request_contract, response_contract).call()
    except ResponseError as error:
        raise CallError(error.message, error.original_exception)
    except RemoteCallError as error:
        raise CallError(error.message, error.original_exception)
    return response


def authorization():
    api_name = "GET_TOKEN"

    request_contract = BNIOpgAuthRequest(url=generate_url(api_name), method="POST")
    request_contract.payload = {"grant_type": "client_credentials"}

    response_contract = BNIOpgAuthResponse
    response = call(request_contract, response_contract)

    access_token = response["data"]["access_token"]
    return access_token
