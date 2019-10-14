"""
    Excute HTTP Call
    ____________________
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


class FetchError(BaseError):
    """ raised when fetch error """


def fetch(request, response):
    """ execute http request """
    try:
        debug_request()
        resp = requests.request(**request.to_representation())
        logging.info("%s %s", request.method, request.url)
        logging.info("HEADER : %s", resp.request.headers)
        logging.info("PAYLOAD : %s", request.payload)
    except requests.exceptions.Timeout as error:
        raise FetchError("TIMEOUT", error)
    except requests.exceptions.SSLError as error:
        raise FetchError("SSL_ERROR", error)
    except requests.exceptions.ConnectionError as error:
        raise FetchError("CONNECTION_ERROR", error)
    else:
        logging.info("HTTP_STATUS : %s", resp.status_code)
        logging.info("RESPONSE : %s", resp.text)
        response.set(resp)
    return response.to_representation()
