"""
    Test Base HTTP response
"""
from unittest.mock import Mock, patch
import pytest

from task.bank.lib.response import HTTPResponse
from task.bank.lib.response import StatusCodeError, InvalidResponseError

from tests.reusable.setup import create_http_response


class TestHTTPResponse:
    def test_validate_success_status_code(self):
        # validate successfull http status_code code
        mock_http_response = create_http_response(200)

        response = HTTPResponse()
        response.set(mock_http_response)

        assert response.validate_status_code()

    def test_validate_failed_status_code(self):
        # first test error http code with JSON
        mock_http_response = create_http_response(400)

        with pytest.raises(StatusCodeError):
            response = HTTPResponse()
            response.set(mock_http_response)
            response.validate_status_code()

        mock_http_response = create_http_response(200)

        response = HTTPResponse()
        response.set(mock_http_response)
        assert response.validate_status_code()

    def test_validate_data(self):
        mock_http_response = create_http_response(
            200,
            {
                "data": "Your request has been processed\
            successfully"
            },
        )

        response = HTTPResponse()
        response.set(mock_http_response)

        assert response.validate_data()

        mock_http_response = create_http_response(200, "request success")

        response = HTTPResponse()
        response.set(mock_http_response)
        assert response.validate_data()

        mock_http_response = Mock()
        # simujlate error parsing json
        mock_http_response.json.side_effect = ValueError

        with pytest.raises(InvalidResponseError):
            response = HTTPResponse()
            response.set(mock_http_response)
            response.validate_data()

    def test_to_representation_ok(self):
        """ test successfull request """
        mock_http_response = Mock(status_code=200)
        expected_data = {"data": "Your request has been processed successfully"}
        mock_http_response.json.return_value = expected_data

        response = HTTPResponse()
        response.set(mock_http_response)
        assert response.to_representation() == expected_data

    def test_to_representation_bad_request(self):
        """ test successfull request """
        mock_http_response = Mock(status_code=400)
        expected_data = {"error": "some bad request"}
        mock_http_response.json.return_value = expected_data

        with pytest.raises(StatusCodeError):
            response = HTTPResponse()
            response.set(mock_http_response)
            response.to_representation()

    def test_to_representation_internal_error(self):
        """ test successfull request """
        mock_http_response = Mock(status_code=500)
        expected_data = {"error": "internal server error"}
        mock_http_response.json.return_value = expected_data

        with pytest.raises(StatusCodeError):
            response = HTTPResponse()
            response.set(mock_http_response)
            response.to_representation()
