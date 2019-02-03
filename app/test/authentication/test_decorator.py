"""
    Test Decorator
"""
#pylint: disable=import-error
#pylint: disable=unused-import
from unittest.mock import patch, Mock

from app.test.base import BaseTestCase
from app.api.models import User

# import all decorator
from app.api.authentication.decorator import admin_required
from app.api.authentication.decorator import refresh_token_only
from app.api.authentication.decorator import token_required
from app.api.authentication.decorator import get_token_payload
from app.api.authentication.decorator import get_current_token

from app.api.exception.authentication.exceptions import TokenError
from app.api.exception.authentication.exceptions import RevokedTokenError
from app.api.exception.authentication.exceptions import SignatureExpiredError
from app.api.exception.authentication.exceptions import InvalidTokenError

# import all routes

class TestAuthDecorator(BaseTestCase):
    """ test auth decorator"""

    def test_admin_required(self):
        func = Mock()
        decorated = admin_required(func)
