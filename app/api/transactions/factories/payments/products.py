"""
    Payment Product
    _____________
"""
from abc import ABC

from sqlalchemy.exc import IntegrityError

from app.api import db

class AbstractPayment(ABC):
    """ abstract class for Payment Product """
    def __init__(self):
        self.payment = None

    def load(self, payment):
        """ load payment model into abstract object so it can be accessed """
        self.payment = payment

    def create(self):
        """ insert actual model into database """
        try:
            db.session.add(self.payment)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            return None
        return self.payment
    #end def

class CreditPayment(AbstractPayment):
    """" concrete class of Abstract payment that represent Credit Payment """
    def create(self):
        """ override super class create method"""
        # add payment flag as CREDIT = True
        self.payment.payment_type = True
        payment = super().create()
        return payment
    #end def

class DebitPayment(AbstractPayment):
    """" concrete class of Abstract payment that represent Debit Payment """
    def create(self):
        """ override super class create method"""
        # add payment flag as DEBIT = True
        self.payment.payment_type = False
        payment = super().create()
        return payment
    #end def
