"""
    Remote Call
    __________________
    module to handle HTTP Execution to all kind of external API
"""
import logging
import requests

from task.bank.lib.exceptions import BaseError


def debug_request():
    """Switches on logging of the requests module."""
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")
    stream_handler.setFormatter(stream_formatter)
    requests_log.addHandler(stream_handler)


class RemoteCallError(BaseError):
    """ exception raised when there are something wrong with http call """


class RemoteCall:
    """ Base Class for all Remote Call """

    def __init__(self, request, response):
        """
            Need HTTP Request Object
            HTTP Response Object
        """
        self.request = request
        self.response = response

    def pre_call(self):
        """ will trigger before http call executed"""
        pass

    def after_call(self):
        """ will trigger after http call executed"""
        pass

    def call(self):
        """ execute http request """
        try:
            debug_request()
            resp = requests.request(**self.request.to_representation())
            logging.info("%s %s", self.request.method, self.request.url)
            logging.info("HEADER : %s", resp.request.headers)
            logging.info("PAYLOAD : %s", self.request.payload)
        except requests.exceptions.Timeout as error:
            raise RemoteCallError("TIMEOUT", error)
        except requests.exceptions.SSLError as error:
            raise RemoteCallError("SSL_ERROR", error)
        except requests.exceptions.ConnectionError as error:
            raise RemoteCallError("CONNECTION_ERROR", error)
        else:
            logging.info("HTTP_STATUS : %s", resp.status_code)
            logging.info("RESPONSE : %s", resp.text)
        return self.response(resp).to_representation()
