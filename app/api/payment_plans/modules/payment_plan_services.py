"""
    Payment Plan Services
    _______________
"""
# database
from app.api import db
# models
from app.api.models import *
# bank account
from app.api.users.modules.bank_account_services import BankAccountServices
from app.api.plans.modules.plan_services import PlanServices
# serializer
from app.api.serializer import PaymentPlanSchema
# http response
from app.api.http_response import *
# utility
from app.api.utility.utils import validate_uuid
# exceptions
from app.api.error.http import *
from sqlalchemy.exc import IntegrityError
# configuration
from app.config import config

class PaymentPlanServices:
    """ Payment Plan Services Class"""
    error_response = config.Config.ERROR_CONFIG

    def __init__(self, wallet_id=None, payment_plan_id=None):
        if wallet_id is not None:
            wallet_record = Wallet.query.filter_by(id=validate_uuid(wallet_id)).first()
            if wallet_record is None:
                raise RequestNotFound(self.error_response["WALLET_NOT_FOUND"]["TITLE"],
                                      self.error_response["WALLET_NOT_FOUND"]["MESSAGE"])
            #end if
            self.wallet = wallet_record
        # end if

        if payment_plan_id is not None:
        # look up user only if user_id is set
            payment_plan = PaymentPlan.query.filter_by(
                id=payment_plan_id,
            ).first()
            if payment_plan is None:
                raise RequestNotFound(
                    self.error_response["PAYMENT_PLAN_NOT_FOUND"]["TITLE"],
                    self.error_response["PAYMENT_PLAN_NOT_FOUND"]["MESSAGE"]
                )
            # end if
            self.payment_plan = payment_plan
        # end if
    #end def

    def add(self, payment_plan):
        """
            add new payment_plan
            add plan
        """
        response = {
            "payment_plan_id" : None,
            "bank_account_id" : None
        }
        try:
            # extract plans
            plans = payment_plan.plans

            # set wallet id
            payment_plan.wallet_id = self.wallet.id
            db.session.add(payment_plan)
            db.session.commit()

            # register the destination as bank account if not created
            # defaultly register as BNI VA
            repayment_va_account = BankAccount.query.filter_by(account_no=payment_plan.destination).first()
            if repayment_va_account is None:
                repayment_va_account = BankAccount(
                    label="VA Repayment Account",
                    name=self.wallet.user.name,
                    account_no=payment_plan.destination
                )
                result = BankAccountServices(
                    str(self.wallet.user.id), "009"
                ).add(repayment_va_account)[0]
                response["bank_account_id"] = result["data"]["bank_account_id"]
            # end if

            # adding plan
            for plan in plans:
                result = PlanServices(payment_plan.id).add(plan)
            # end for
        except IntegrityError as error:
            #print(err.orig)
            db.session.rollback()
            raise UnprocessableEntity(
                self.error_response["DUPLICATE_PAYMENT_PLAN"]["TITLE"],
                self.error_response["DUPLICATE_PAYMENT_PLAN"]["MESSAGE"]
            )
        # end try
        response["payment_plan_id"] = payment_plan.id
        return created(response)
        #end try

    @staticmethod
    def show():
        """ show all stored payment_plan """
        payment_plans = PaymentPlan.query.all()
        response = PaymentPlanSchema(many=True).dump(payment_plans).data
        return ok(response)
    #end def

    def info(self):
        """ return single payment plan """
        payment_plan = PaymentPlanSchema().dump(self.payment_plan).data
        return ok(payment_plan)
    #end def

    def update(self, params):
        """ update payment plan """
        self.payment_plan.destination = params["destination"]
        self.payment_plan.wallet_id = self.wallet.id

        status = bool(params["status"] == "ACTIVE")
        self.payment_plan.status = status

        db.session.commit()
        return no_content()
    #end def

    def remove(self):
        """ remove payment plan """
        try:
            db.session.delete(self.payment_plan)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
        #end try
        return no_content()
    #end def
#end class