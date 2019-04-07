"""
    Integration Testing between services & routes
"""
import uuid
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api import db

class TestProductRoutes(BaseTestCase):
    """ Test Class for Product Routes"""
    """
        CREATE Product
    """
    def test_create_product_with_custom_id(self):
        """ Create product CASE 1 : Successfully created product with custom id """
        params = {
            "id"           : "modana-cepat-loan",
            "name"         : "Modana Cepat",
            "description"  : "Product Description",
            "types"        : "SERVICE",
        }
        result = self.create_product(params, "some-api-key")
        response = result.get_json()
        print(response)
        self.assertEqual(response['data']['product_id'], params['id'])

    def test_create_product_without_custom_id(self):
        """ Create product CASE 2 : Successfully created product without custom id """
        params = {
            "name"         : "Modana Cepat",
            "description"  : "Product Description",
            "types"        : "SERVICE",
        }
        result = self.create_product(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['product_id'])

    """
        GET PRODUCTS
    """

    def test_get_products(self):
        """ get products CASE 1 : Successfully get all products"""
        params = {
            "name"         : "Modana Cepat",
            "description"  : "Product Description",
            "types"        : "SERVICE",
        }
        result = self.create_product(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['product_id'])

        result = self.get_products("some-api-key")
        response = result.get_json()
        self.assertTrue(response['data'])

    """
        GET PRODUCT
    """
    def test_get_product(self):
        """ GET product CASE 1 : Successfully get product """
        params = {
            "name"         : "Modana Cepat",
            "description"  : "Product Description",
            "types"        : "SERVICE",
        }
        result = self.create_product(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['product_id'])
        product_id = response['data']['product_id']

        result = self.get_product(product_id, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data'])

    def test_get_product_invalid_product_id(self):
        """ GET product CASE 2 : Failed get product because invalid product id"""
        product_id = str(uuid.uuid4())

        result = self.get_product(product_id, "some-api-key")
        response = result.get_json()
        self.assertEqual(result.status_code, 404)

    """
        REMOVE PRODUCT
    """
    def test_remove_product(self):
        """ DELETE product CASE 1 : Successfully remove product """
        params = {
            "name"         : "Modana Cepat",
            "description"  : "Product Description",
            "types"        : "SERVICE",
        }
        result = self.create_product(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['product_id'])
        product_id = response['data']['product_id']

        result = self.remove_product(product_id, "some-api-key")
        self.assertEqual(result.status_code, 204) # no content

    def test_remove_product_failed(self):
        """ DELETE product CASE 2 : Failed remove product because invalid product id"""
        product_id = str(uuid.uuid4())

        result = self.remove_product(product_id, "some-api-key")
        response = result.get_json()
        self.assertEqual(result.status_code, 404)

    """
        UPDATE PRODUCT
    """
    def test_update_product(self):
        """ PUT product CASE 1 : Successfully update product """
        params = {
            "name"         : "Modana Cepat",
            "description"  : "Product Description",
            "types"        : "SERVICE",
        }
        result = self.create_product(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['product_id'])
        product_id = response['data']['product_id']

        params = {
            "name"         : "Modana Super Cepat",
            "description"  : "Product more Description",
            "types"        : "SERVICE",
        }

        result = self.update_product(product_id, params, "some-api-key")
        self.assertEqual(result.status_code, 204)
