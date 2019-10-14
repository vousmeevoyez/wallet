"""
    Request Factory
    __________________
    factory method to handle request creation
"""
from task.bank.lib.factory import Factory
from task.bank.factories.request.opg.request import (
    BNIOpgAuthRequest,
    BNIOpgRequest
)
from task.bank.factories.request.va.request import (
    BNICreditEcollectionRequest,
    BNIDebitEcollectionRequest
)


def generate_request(external_resource):
    """ generate request object """
    factory = Factory()
    factory.register("BNI_AUTH_OPG", BNIOpgAuthRequest)
    factory.register("BNI_OPG", BNIOpgRequest)
    factory.register("BNI_CREDIT_VA", BNICreditEcollectionRequest)
    factory.register("BNI_DEBIT_VA", BNIDebitEcollectionRequest)

    generator = factory.get(external_resource)
    return generator
