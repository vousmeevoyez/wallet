"""
    Plan Services
    _______________
"""
# database
from app.api  import db
# models
from app.api.models import *
# serializer
from app.api.serializer import PlanSchema
# http response
from app.api.http_response import *
# utility
from app.api.utility.utils import validate_uuid
# exceptions
from app.api.error.http import *
from sqlalchemy.exc import IntegrityError
# configuration
from app.config import config

class PlanServices:
    """ Plan Services Class"""
    error_response = config.Config.ERROR_CONFIG

    def __init__(self, payment_plan_id=None, plan_id=None):
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

        if plan_id is not None:
        # look up user only if user_id is set
            plan = Plan.query.filter_by(
                id=plan_id,
            ).first()
            if plan is None:
                raise RequestNotFound(
                    self.error_response["PLAN_NOT_FOUND"]["TITLE"],
                    self.error_response["PLAN_NOT_FOUND"]["MESSAGE"]
                )
            # end if
            self.plan = plan
        # end if
    #end def

    def add(self, plan):
        """
            add plan
        """
        try:
            # extract plans
            plan.payment_plan_id = self.payment_plan.id

            db.session.add(plan)
            db.session.commit()
        except IntegrityError as error:
            #print(err.orig)
            db.session.rollback()
            raise UnprocessableEntity(
                self.error_response["DUPLICATE_PLAN"]["TITLE"],
                self.error_response["DUPLICATE_PLAN"]["MESSAGE"]
            )
        # end try
        response = {
            "plan_id" : plan.id
        }
        return created(response)
        #end try

    @staticmethod
    def show():
        """ show all stored plan """
        plans = Plan.query.all()
        response = PlanSchema(many=True).dump(plans).data
        return ok(response)
    #end def

    def info(self):
        """ return single plan """
        plan = PlanSchema().dump(self.plan).data
        return ok(plan)
    #end def

    def update(self, plan):
        """ update plan """
        self.plan.amount = plan.amount
        self.plan.due_date = plan.due_date
        self.plan.type = plan.type

        db.session.commit()
        return no_content()
    #end def

    def update_status(self, params):
        """ update plan status """
        status = None
        if params["status"] == "FAILED":
            status = 4
        elif params["status"] == "PAID":
            status = 5
        elif params["status"] == "STOPPED":
            status = 6
        # end if

        self.plan.status = status

        db.session.commit()
        return no_content()
    #end def

    def remove(self):
        """ remove plan """
        try:
            db.session.delete(self.plan)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
        #end try
        return no_content()
    #end def
#end class
