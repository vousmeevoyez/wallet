"""
    Request Factory
    __________________
    factory method to handle provider creation
"""
from task.bank.lib.factory import Factory
from task.bank.factories.provider.opg.provider import BNIOpgProviderBuilder
from task.bank.factories.provider.va.provider import BNIVaProvider


def generate_provider(external_resource):
    """ generate provider object """
    factory = Factory()
    factory.register("BNI_OPG", BNIOpgProviderBuilder())
    factory.register("BNI_VA", BNIVaProvider)

    service = factory.get(external_resource)
    return service
