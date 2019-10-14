"""
    Testing Core
    ______________
"""
from unittest.mock import patch

from app.api.request_schema import UserRequestSchema
from app.api.core import CoreRoutes

from marshmallow.exceptions import ValidationError

'''
@patch("flask.request.get_json")
def test_payload_raw(mock_flask_request):
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
        assert result, request_data


@patch("flask.request.get_json")
def test_payload_with_schema(mock_flask_request):
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
    assert result == request_data
'''
