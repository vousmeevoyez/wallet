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

from app.api.payment_plans import api
#serializer
from app.api.serializer import PaymentPlanSchema
# request schema
from app.api.request_schema import PaymentPlanRequestSchema
# wallet modules
from app.api.payment_plans.modules.payment_plan_services import PaymentPlanServices
# authentication
from app.api.auth.decorator import api_key_required
# exceptions
from app.api.error.http import BadRequest
# configuration
from app.config import config

class BaseRoutes(Resource):
    """ base routes class """
    error_response = config.Config.ERROR_CONFIG

@api.route('/')
class PaymentPlanRoutes(BaseRoutes):
    """
        Payment Plan
        /payment_plans
    """
    @api_key_required
    def post(self):
        """ Endpoint for creating payment plan """
        request_data = PaymentPlanRequestSchema.parser.parse_args(strict=True)
        try:
            payment_plan = PaymentPlanSchema(strict=True).load(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        # end try
        response = PaymentPlanServices(request_data["wallet_id"]).add(payment_plan.data)
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
class PaymentPlanInfoRoutes(BaseRoutes):
    """
        Payment Plan
        /payment_plans
    """
    @api_key_required
    def put(self, payment_plan_id):
        """ Endpoint for updating payment plan """
        request_data = PaymentPlanRequestSchema.parser.parse_args(strict=True)
        try:
            payment_plan = PaymentPlanSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        # end try
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
