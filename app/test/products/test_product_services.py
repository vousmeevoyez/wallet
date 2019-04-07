"""
    Test Product Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base import BaseTestCase

from app.api.models import *

from app.api.error.http import *

from app.api.products.modules.product_services import ProductServices

class TestProductServices(BaseTestCase):
    """ Test Class for Product Services"""

    def test_add_product(self):
        """ test method for creating product"""
        product = Product(
            name="Modana Cepat",
            description="Quick Payday Loan"
        )
        result = ProductServices().add(product)[0]
        self.assertTrue(result['data']['product_id'])

    def test_show_product(self):
        """ test method for show all available product"""
        product = Product(
            name="Modana Cepat",
            description="Quick Payday Loan"
        )
        result = ProductServices().add(product)[0]
        self.assertTrue(result['data']['product_id'])

        product = Product(
            name="Modana Cicil",
            description="Payday Loan"
        )
        result = ProductServices().add(product)[0]
        self.assertTrue(result['data']['product_id'])

        result = ProductServices.show()[0]
        self.assertTrue(len(result['data']) > 0)

    def test_info_product(self):
        """ test method for info product"""
        product = Product(
            name="Modana Cepat",
            description="Quick Payday Loan"
        )
        result = ProductServices().add(product)[0]
        product_id = result['data']['product_id']
        self.assertTrue(result['data']['product_id'])

        result = ProductServices(product_id).info()[0]
        self.assertTrue(result['data'])

    def test_remove_product(self):
        """ test method for remove product"""
        product = Product(
            name="Modana Cepat",
            description="Quick Payday Loan"
        )
        result = ProductServices().add(product)[0]
        product_id = result['data']['product_id']
        self.assertTrue(result['data']['product_id'])

        result = ProductServices(product_id).remove()[1]
        self.assertEqual(result, 204)

    def test_update_product(self):
        """ test method for updating product"""
        product = Product(
            name="Modana Cepat",
            description="Quick Payday Loan"
        )
        result = ProductServices().add(product)[0]
        product_id = result['data']['product_id']
        self.assertTrue(result['data']['product_id'])

        data = {
            "name" : "Mocepat",
            "description" : "Some Description",
            "types" : 2,
            "status" : True
        }
        result = ProductServices(product_id).update(data)[1]
        self.assertEqual(result, 204)
