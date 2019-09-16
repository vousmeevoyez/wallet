"""
    Testing Core
    ______________
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase
from app.api.serializer import *
from app.api.models import *
from app.api import db
from app.api.request_schema import *
from app.api.core import CoreRoutes

from marshmallow.exceptions import ValidationError


class TestCoreRoutes(BaseTestCase):
    @patch("flask.request.get_json")
    def test_payload_raw(self, mock_flask_request):
        """ test our reusable payload function to handle flask request """
        request_data = {
            "username": "Lisa",
            "name": "Lisa",
            "phone_ext": "62",
            "phone_number": "81219644314",
            "email": "lisa@bp.com",
            "password": "password",
            "pin": "123456",
            "role": "USER",
            "label": "PERSONAL",
        }
        mock_flask_request.return_value = request_data

        core_routes = CoreRoutes()
        core_routes.__schema__ = UserRequestSchema

        result = core_routes.payload(raw=True)
        self.assertEqual(result, request_data)

    @patch("flask.request.get_json")
    def test_payload_with_schema(self, mock_flask_request):
        """ test our reusable payload function to handle flask request """
        request_data = {
            "username": "Lisa",
            "name": "Lisa",
            "phone_ext": "62",
            "phone_number": "81219644314",
            "email": "lisa@bp.com",
            "password": "password",
            "pin": "123456",
            "role": "USER",
            "label": "PERSONAL",
        }
        mock_flask_request.return_value = request_data

        core_routes = CoreRoutes()
        core_routes.__schema__ = UserRequestSchema

        result = core_routes.payload()
        self.assertEqual(result, request_data)
