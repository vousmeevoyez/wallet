"""
    Response Factory
    __________________
    factory method to handle request creation
"""
from task.bank.lib.factory import Factory
from task.bank.factories.response.opg.response import (
    BNIOpgAuthResponse,
    BNIOpgResponse
)
from task.bank.factories.response.va.response import (
    BNICreditEcollectionResponse,
    BNIDebitEcollectionResponse
)


def generate_response(external_resource):
    """ generate response object """
    factory = Factory()
    factory.register("BNI_AUTH_OPG", BNIOpgAuthResponse)
    factory.register("BNI_OPG", BNIOpgResponse)
    factory.register("BNI_CREDIT_VA", BNICreditEcollectionResponse)
    factory.register("BNI_DEBIT_VA", BNIDebitEcollectionResponse)

    generator = factory.get(external_resource)
    return generator
