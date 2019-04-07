"""
    Product Services
    ________________
    This is module that serve everything related to product
"""
#pylint: disable=bad-whitespace
#pylint: disable=no-self-use
from sqlalchemy.exc import IntegrityError

from app.api import db
# helper
from app.api.utility.utils import validate_uuid
# models
from app.api.models import *
# serializer
from app.api.serializer import ProductSchema
# http error
from app.api.http_response import *
# exception
from app.api.error.http import *
# configuration
from app.config import config

class ProductServices:
    """ Product Services Class"""
    error_response = config.Config.ERROR_CONFIG

    def __init__(self, product_id=None):
        if product_id is not None:
            product_record = Product.query.filter_by(id=product_id,
                                                    status=True).first()
            if product_record is None:
                raise RequestNotFound(self.error_response["PRODUCT_NOT_FOUND"]["TITLE"],
                                      self.error_response["PRODUCT_NOT_FOUND"]["MESSAGE"])
            #end if
            self.product = product_record

    def add(self, product):
        """ create product record """
        try:
            db.session.add(product)
            db.session.commit()
        except IntegrityError as error:
            #print(error.origin)
            db.session.rollback()
            raise UnprocessableEntity(self.error_response["DUPLICATE_PRODUCT"]["TITLE"],
                                      self.error_response["DUPLICATE_PRODUCT"]["MESSAGE"])
        #end try
        response = {
            "product_id" : product.id
        }
        return created(response)
    #end def

    def update(self, params):
        """ update product record """
        self.product.name = params["name"]
        self.product.description = params["description"]

        db.session.commit()
        return no_content()
    #end def

    @staticmethod
    def show():
        """ return all product """
        products = Product.query.filter_by(status=True).all()
        response = ProductSchema(many=True).dump(products).data
        return ok(response)
    #end def

    def info(self):
        """ return product info"""
        product = ProductSchema().dump(self.product).data
        return ok(product)
    #end def

    def remove(self):
        """ remove product """
        db.session.delete(self.product)
        db.session.commit()
        return no_content()
    #end def
#end class
