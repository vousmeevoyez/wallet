"""
    Provider
    _________________
"""

from task.bank.lib.remote_call import fetch
from task.bank.factories.factory import generate_request_response

# base exceptions
from task.bank.lib.exceptions import BaseError
# response exceptions
from task.bank.lib.response import (
    StatusCodeError,
    FailedResponseError,
    InvalidResponseError,
    ResponseError
)
# remote call exceptions
from task.bank.lib.remote_call import FetchError


class ProviderError(BaseError):
    """ error raised when provider error """


class BaseProvider:
    """ Base Provider """

    service_url = None
    service_port = None
    contract = None

    def __init__(self, *args, **kwargs):
        # generate request response
        request, response = generate_request_response(self.contract)
        self._request_contract = request
        self._response_contract = response
        # build url
        self._url = self.build_url()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def request_contract(self):
        return self._request_contract

    @request_contract.setter
    def request_contract(self, contract):
        self._request_contract = contract

    @property
    def response_contract(self):
        return self._response_contract

    @response_contract.setter
    def response_contract(self, contract):
        self._response_contract = contract

    def build_url(self, *args, **kwargs):
        """ method to build right service url!"""
        url = self.service_url
        if self.service_port is not None:
            # if we connect to specific port we need to add it as path to
            url = self.service_url + ":" + self.service_port
        return url

    def prepare_request(self, **kwargs):
        """ prepare parameter and extract it into right request """
        self.request_contract.url = kwargs["url"]
        self.request_contract.method = kwargs["method"]
        self.request_contract.payload = kwargs["payload"]

    def call(self):
        """ wrapper function to encapsulate request & response contract!"""
        try:
            response = fetch(
                self.request_contract,
                self.response_contract
            )
        except FetchError as error:
            raise ProviderError(error.message, error.original_exception)
        except StatusCodeError as error:
            raise ProviderError(error.message, error.original_exception)
        except FailedResponseError as error:
            raise ProviderError(error.message, error.original_exception)
        except InvalidResponseError as error:
            raise ProviderError(error.message, error.original_exception)
        except ResponseError as error:
            raise ProviderError(error.message, error.original_exception)
        # end try
        return response

    def execute(self, **kwargs):
        self.prepare_request(**kwargs)
        return self.call()
