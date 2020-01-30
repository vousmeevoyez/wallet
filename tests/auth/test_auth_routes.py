"""
    Test Authentication Routes
"""
import pytest

from tests.reusable.api_list import *


def test_get_access_token_success(client, setup_user_only):
    """ test success get access token"""
    result = get_access_token(client, "dummyuser", "password")
    response = result.get_json()

    assert result.status_code == 200
    assert response["data"]["access_token"]
    assert response["data"]["refresh_token"]


def test_get_access_token_failed_record_not_found(client):
    """ test failed record not found get access token"""
    result = get_access_token(client, "jennie", "password")
    response = result.get_json()

    assert result.status_code == 404
    assert response["error"] == "USER_NOT_FOUND"


def test_get_access_token_failed_invalid_login(client, setup_user_only):
    """ tes invalid login get access token"""
    result = get_access_token(client, "dummyuser", "pa3sword")
    response = result.get_json()

    assert result.status_code == 401
    assert response["error"] == "INVALID_CREDENTIALS"


def test_get_refresh_token_success(client, setup_user_only):
    """ tes success get refresh token"""
    # login first and get the refersh token
    result = get_access_token(client, "dummyuser", "password")
    response = result.get_json()

    refresh_token = response["data"]["refresh_token"]

    result = get_refresh_token(client, refresh_token)
    response = result.get_json()

    assert result.status_code == 200


def test_get_refresh_token_failed_refresh_token_only(client, setup_user_only):
    """ tes failed get refresh token"""
    # login first and get the refersh token
    result = get_access_token(client, "dummyuser", "password")
    response = result.get_json()

    assert result.status_code == 200
    assert response["data"]["access_token"]
    assert response["data"]["refresh_token"]

    access_token = response["data"]["access_token"]

    result = get_refresh_token(client, access_token)
    response = result.get_json()

    assert result.status_code == 405


def test_get_refresh_token_failed_invalid_token(client, setup_user_only):
    """ test get refresh token using invalid token"""
    refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    result = get_refresh_token(client, refresh_token)
    assert result.status_code == 401


def test_revoke_token_success(client, setup_user_only):
    """ test revoking access token"""
    # login first and get the refersh token
    result = get_access_token(client, "dummyuser", "password")
    response = result.get_json()

    access_token = response["data"]["access_token"]

    result = revoke_token(client, access_token)
    assert result.status_code == 204


def test_revoke_token_failed_invalid_token(client):
    """ test failed revoking access token using invalid token"""
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    result = revoke_token(client, access_token)
    assert result.status_code == 401
