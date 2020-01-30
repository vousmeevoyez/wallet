"""
    Testing Factory Request
    ______________________
"""
import pytest

from task.bank.factories.response.factory import generate_response

from task.bank.lib.response import *

from tests.reusable.setup import create_http_response


class TestResponseFactory:
    """ Testing Factory response Class"""

    def test_create_bni_auth_opg_success(self):

        expected_data = {
            "access_token": "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "resource.WRITE resource.READ",
        }
        mock_http_response = create_http_response(200, expected_data)

        bni_response = generate_response("BNI_AUTH_OPG")
        bni_response.set(mock_http_response)
        bni_response = bni_response.to_representation()

        assert bni_response["access_token"]

    def test_create_bni_auth_opg_failed(self):

        expected_data = {"error": "unauthorized error"}
        mock_http_response = create_http_response(400, expected_data)

        bni_response = generate_response("BNI_AUTH_OPG")
        bni_response.set(mock_http_response)

        with pytest.raises(ResponseError):
            bni_response = bni_response.to_representation()
