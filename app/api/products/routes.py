"""
    Wallet Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods

from flask_restplus     import Resource
from marshmallow import ValidationError

from app.api.products import api
#serializer
from app.api.serializer import *
# request schema
from app.api.request_schema import *
# product modules
from app.api.products.modules.product_services import ProductServices
# exceptions
from app.api.error.http import *
# configuration
from app.config import config

class BaseRoutes(Resource):
    error_response = config.Config.ERROR_CONFIG

@api.route('/')
class ProductAddRoutes(BaseRoutes):
    """
        Product add Routes
        api/v1/products
    """
    def post(self):
        """ Endpoint for creating Product """
        request_data = ProductRequestSchema.parser.parse_args(strict=True)
        try:
            product = ProductSchema(strict=True).load(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)

        response = ProductServices().add(product.data)
        return response
    #end def

    def get(self):
        """ Endpoint for showing all Product """
        response = ProductServices.show()
        return response
    #end def
#end class

@api.route('/<string:product_id>')
class ProductInfoRoutes(BaseRoutes):
    """
        Product add Routes
        api/v1/products/<product_id>
    """
    def get(self, product_id):
        """ Endpoint for getting isngle Product """
        response = ProductServices(product_id).info()
        return response
    #end def

    def delete(self, product_id):
        """ Endpoint for removing Product """
        response = ProductServices(product_id).remove()
        return response
    #end def

    def put(self, product_id):
        """ Endpoint for updating Product """
        request_data = ProductRequestSchema.parser.parse_args(strict=True)
        try:
            product = ProductSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        # end try
        response = ProductServices(product_id).update(request_data)
        return response
    #end def
#end class
