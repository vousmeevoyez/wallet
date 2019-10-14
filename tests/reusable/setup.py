"""
    Fixtures
"""
from unittest.mock import Mock


def create_http_response(status_code, response=None, exception=None):
    """ fixture to create http response """
    http_response = Mock(status_code=status_code)
    http_response.json.return_value = response
    return http_response
