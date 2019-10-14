"""
    Request Response Factory
    _______________________
"""
from task.bank.factories.request.factory import generate_request
from task.bank.factories.response.factory import generate_response


def generate_request_response(external_resource):
    """ handle request and response object creation """
    request = generate_request(external_resource)
    response = generate_response(external_resource)
    return request, response
