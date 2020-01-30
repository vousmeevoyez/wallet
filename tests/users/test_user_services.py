"""
    Test User Services
"""
import pytest

from app.api.users.modules.user_services import UserServices

from app.api.models import *
from app.api import db

from app.lib.http_error import *


""" Test User Services"""


def test_user_add_success():
    """ Test add user """
    params = {
        "username": "roserose",
        "name": "roserose",
        "phone_ext": "62",
        "phone_number": "800212341230",
        "email": "roserosebp@blackpink.com",
        "role_id": 1,
    }
    user = User(**params)
    result = UserServices().add(user, "password", "123456", "LABEL")
    assert result[1] == 201  # created


def test_user_add_failed_duplicate(setup_user_only):
    """ test fail adding user by trying add same account"""
    params = {
        "username": "dummyuser",
        "name": "jennie",
        "phone_ext": "62",
        "phone_number": "81212341235",
        "email": "jennie@blackpink.com",
        "role_id": 1,
    }
    user = User(**params)
    with pytest.raises(UnprocessableEntity):
        UserServices().add(user, "password", "123456", "LABEL")


def test_user_list_success():
    """ test get list of users"""
    result = UserServices().show({})
    assert len(result) > 0


def test_user_info_success(setup_user_only):
    """ test get single user info"""
    user_id = str(setup_user_only.id)

    result = UserServices(user_id).info()
    assert result[0]["data"]


def test_user_info_failed_record_not_found():
    """ test get single user info but user not found"""
    with pytest.raises(BadRequest):
        UserServices("12345").info()


def test_update_user_success(setup_user_only):
    """ test updating user information """
    user_id = str(setup_user_only.id)
    params = {
        "name": "jisooo",
        "phone_ext": "62",
        "phone_number": "81212222222",
        "email": "jisooo@blackpink.com",
        "password": "password",
    }

    result = UserServices(user_id).update(params)
    assert result[1] == 204

    result = UserServices(user_id).info()
    print(result)


def test_update_user_old(setup_user_only):
    """ test updating user information """
    user_id = str(setup_user_only.id)

    params = {
        "name": "jisooo",
        "phone_ext": "62",
        "phone_number": "81212222222",
        "email": "jisooo@blackpink.com",
    }
    with pytest.raises(UnprocessableEntity):
        UserServices(user_id).update(params)


def test_remove_user_success(setup_user_only):
    """ test removing user """
    user_id = str(setup_user_only.id)

    result = UserServices(user_id).remove()
    assert result[1] == 204  # no content

    with pytest.raises(RequestNotFound):
        result = UserServices(user_id).info()


def test_remove_user_failed_not_found():
    """ test removing user but not found"""
    with pytest.raises(BadRequest):
        UserServices("1234").info()
