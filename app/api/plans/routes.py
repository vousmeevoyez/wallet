"""
    Payment Plan Routes
    _______________
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods
#pylint: disable=no-name-in-module

from flask_restplus import Resource
from marshmallow import ValidationError

from app.api.plans import api
#serializer
from app.api.serializer import PlanSchema
# request schema
from app.api.request_schema import PlanRequestSchema, UpdatePlanRequestSchema
# wallet modules
from app.api.plans.modules.plan_services import PlanServices
# authentication
from app.api.auth.decorator import api_key_required
# exceptions
from app.api.error.http import BadRequest
# configuration
from app.config import config

class BaseRoutes(Resource):
    """ base class for routes """
    error_response = config.Config.ERROR_CONFIG

@api.route('/')
class PlanRoutes(BaseRoutes):
    """
        Plan
        /plans
    """
    @api_key_required
    def post(self):
        """ Endpoint for creating plan """
        request_data = PlanRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = ("status")
            plan = PlanSchema(strict=True).load(request_data, partial=excluded)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        # end try
        response = PlanServices(request_data['payment_plan_id']).add(plan.data)
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
class PaymentPlanInfoRoutes(BaseRoutes):
    """
        Plan
        /plans
    """
    @api_key_required
    def put(self, plan_id):
        """ Endpoint for updating plan """
        request_data = PlanRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = ("status")
            payment_plan = PlanSchema(strict=True).load(request_data,
                                                        partial=excluded)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        # end try
        response = PlanServices(plan_id=plan_id).update(payment_plan.data)
        return response
    #end def

    @api_key_required
    def patch(self, plan_id):
        """ Endpoint for patching plan status """
        request_data = UpdatePlanRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = ("id", "due_date", "type", "amount")
            payment_plan = PlanSchema(strict=True).validate(request_data,
                                                            partial=excluded)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        # end try
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
