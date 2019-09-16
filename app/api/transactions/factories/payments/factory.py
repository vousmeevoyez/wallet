from app.api.transactions.factories.payments.products import CreditPayment, DebitPayment


class PaymentFactory:
    """ payment factory """

    def __init__(self):
        self._creators = {}

    def register(self, type_, creator):
        """ register all known creator using this method """
        self._creators[type_] = creator

    def get(self, type_):
        """ get creator """
        creator = self._creators.get(type_)
        if not creator:
            raise ValueError(type_)
        return creator()


def generate_payment(payment, type_):
    """ generate payment by passing Payment Model and Payment Type """
    factory = PaymentFactory()
    factory.register("CREDIT", CreditPayment)
    factory.register("DEBIT", DebitPayment)

    generator = factory.get(type_)
    payment.load(generator)
    return generator.create()
