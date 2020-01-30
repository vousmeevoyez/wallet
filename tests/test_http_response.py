"""
    Test HTTP Response
"""

from app.lib.http_response import *


""" HTTP Response test class"""


def test_no_content():
    """ test no content HTTP response """
    result = no_content()
    assert result[1] == 204


def test_created():
    """ test created HTTP response """
    result = created()
    assert result[1] == 201


def test_created_message_data():
    """ test created HTTP response and set data and set message"""
    result = created("some data", "some message")
    assert result[1] == 201
    assert result[0]["data"]
    assert result[0]["message"]


def test_accepted():
    """ test accepted HTTP response """
    result = accepted({"data": "some data"})

    assert result[1] == 202
    assert result[0]["data"]


def test_ok():
    """ test okHTTP response """
    result = ok({"data": "some data"})

    assert result[1] == 200
    assert result[0]["data"]
