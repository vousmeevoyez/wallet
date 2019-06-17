"""
    Payment Plan Routes
    _______________
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods
#pylint: disable=no-name-in-module
from app.api.core import Routes

from app.api.payment_plans import api
#serializer
from app.api.serializer import PaymentPlanSchema
# request schema
from app.api.request_schema import PaymentPlanRequestSchema
# wallet modules
from app.api.payment_plans.modules.payment_plan_services import PaymentPlanServices
# authentication
from app.api.auth.decorator import api_key_required

@api.route('/')
class PaymentPlanRoutes(Routes):
    """
        Payment Plan
        /payment_plans
    """

    __schema__ = PaymentPlanRequestSchema
    __serializer__ = PaymentPlanSchema()

    @api_key_required
    def post(self):
        """ Endpoint for creating payment plan """
        request_data = self.payload()
        payment_plan = self.serialize(request_data, load=True)

        response = PaymentPlanServices(request_data["wallet_id"]).add(payment_plan)
        return response
    #end def

    @api_key_required
    def get(self):
        """ Endpoint for showing all payment plan """
        response = PaymentPlanServices.show()
        return response
    #end def
#end class

@api.route('/<string:payment_plan_id>')
class PaymentPlanInfoRoutes(Routes):
    """
        Payment Plan
        /payment_plans
    """

    __schema__ = PaymentPlanRequestSchema
    __serializer__ = PaymentPlanSchema()

    @api_key_required
    def put(self, payment_plan_id):
        """ Endpoint for updating payment plan """
        request_data = self.serialize(self.payload())

        response = PaymentPlanServices(
            payment_plan_id=payment_plan_id,
            wallet_id=request_data["wallet_id"]
        ).update(request_data)
        return response
    #end def

    @api_key_required
    def get(self, payment_plan_id):
        """ Endpoint for showing all payment plan """
        response = PaymentPlanServices(payment_plan_id=payment_plan_id).info()
        return response
    #end def

    @api_key_required
    def delete(self, payment_plan_id):
        """ Endpoint for removing payment plan """
        response = PaymentPlanServices(payment_plan_id=payment_plan_id).remove()
        return response
    #end def
#end class
