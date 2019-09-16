"""
    HTTP Request
    __________________
    base reusable class for various HTTP Request
"""
from app.api.const import LOGGING


class HTTPRequest:
    """ represent http request """

    def __init__(self, url, method):
        self._url = url
        self._header = {}
        self._method = method
        self._payload = None
        self.timeout = LOGGING["TIMEOUT"]

    @staticmethod
    def _convert_to_header_convention(key):
        """ special method to convert kwargs into known http header """
        # first convert key into Capitalize
        capitalize = key.title()
        # second convert underscore into dash
        underscore = capitalize.replace("_", "-")
        return underscore

    def to_representation(self):
        # convert object into parsable data
        self.setup_header()
        return {
            "url": self._url,
            "method": self._method,
            "data": self._payload,
            "headers": self._header,
            "timeout": self.timeout,
        }

    def setup_header(self, *args, **kwargs):
        """ setup HTTP request header """
        self._header["Content-Type"] = "application/json"

    @property
    def payload(self):
        """ fetch request payload """
        return self._payload

    @payload.setter
    def payload(self, payload):
        """ set payload """
        self._payload = payload

    @property
    def url(self):
        """ fetch request url """
        return self._url

    @url.setter
    def url(self, url):
        """ set url """
        self._url = url

    @property
    def method(self):
        """ fetch request method """
        return self._method

    @method.setter
    def method(self, method):
        """ set request method """
        self._method = method
