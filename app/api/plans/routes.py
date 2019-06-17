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

from app.api.plans import api
#serializer
from app.api.serializer import PlanSchema
# request schema
from app.api.request_schema import PlanRequestSchema, UpdatePlanRequestSchema
# wallet modules
from app.api.plans.modules.plan_services import PlanServices
# authentication
from app.api.auth.decorator import api_key_required

@api.route('/')
class PlanRoutes(Routes):
    """
        Plan
        /plans
    """
    __schema__ = PlanRequestSchema
    __serializer__ = PlanSchema(exclude=("status"))

    @api_key_required
    def post(self):
        """ Endpoint for creating plan """
        request_data = self.payload()
        plan = self.serialize(request_data, load=True)

        response = PlanServices(request_data['payment_plan_id']).add(plan)
        return response
    #end def

    @api_key_required
    def get(self):
        """ Endpoint for showing all payment plan """
        response = PlanServices.show()
        return response
    #end def
#end class

@api.route('/<string:plan_id>')
class PaymentPlanInfoRoutes(Routes):
    """
        Plan
        /plans
    """

    __schema__ = PlanRequestSchema
    __serializer__ = PlanSchema(exclude=("status"))

    @api_key_required
    def put(self, plan_id):
        """ Endpoint for updating plan """
        request_data = self.payload()
        plan = self.serialize(request_data, load=True)

        response = PlanServices(plan_id=plan_id).update(plan)
        return response
    #end def

    @api_key_required
    def patch(self, plan_id):
        """ Endpoint for patching plan status """

        self.__schema__ = UpdatePlanRequestSchema
        self.__serializer__ = PlanSchema(exclude=("id", "due_date", "type", "amount"))

        request_data = self.serialize(self.payload())

        response = PlanServices(plan_id=plan_id).update_status(request_data)
        return response
    #end def

    @api_key_required
    def get(self, plan_id):
        """ Endpoint for showing all plan """
        response = PlanServices(plan_id=plan_id).info()
        return response
    #end def

    @api_key_required
    def delete(self, plan_id):
        """ Endpoint for removing plan """
        response = PlanServices(plan_id=plan_id).remove()
        return response
    #end def
#end class
