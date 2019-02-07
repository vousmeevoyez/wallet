"""
    Test HTTP Response
"""
from app.test.base  import BaseTestCase

from app.api.http_response import no_content
from app.api.http_response import created
from app.api.http_response import accepted
from app.api.http_response import error_response
from app.api.http_response import bad_request
from app.api.http_response import unauthorized
from app.api.http_response import request_not_found
from app.api.http_response import insufficient_scope
from app.api.http_response import unprocessable_entity
from app.api.http_response import method_not_allowed
from app.api.http_response import internal_error
from app.api.http_response import bad_gateway
from app.api.http_response import service_unavailable

class TestHTTPResponse(BaseTestCase):
    """ HTTP Response test class"""

    def test_no_content(self):
        """ test no content HTTP response """
        result = no_content()
        self.assertEqual(result[1], 204)

    def test_created(self):
        """ test created HTTP response """
        result = created()
        self.assertEqual(result[1], 201)

    def test_created_message_data(self):
        """ test created HTTP response and set data and set message"""
        result = created("some data", "some message")
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]["data"])
        self.assertTrue(result[0]["message"])

    def test_accepted(self):
        """ test accepted HTTP response """
        result = accepted("message")
        self.assertEqual(result[1], 202)
        self.assertTrue(result[0]["message"])

    def test_error_response(self):
        """ test error_response """
        result = error_response(404, "some error", "some message", "some\
                                details")
        self.assertEqual(result[1], 404)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

        result = error_response(404, "some error", "some message", None) 
        self.assertEqual(result[1], 404)

    def test_bad_request(self):
        """ test bad request """
        result = bad_request(None, "some message", "some details")

        self.assertEqual(result[1], 400)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

    def test_unathorized(self):
        """ test unathorized """
        result = unauthorized(None, "some message", "some details")

        self.assertEqual(result[1], 401)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

    def test_request_not_found(self):
        """ test request_not_found"""
        result = request_not_found(None, "some message", "some details")

        self.assertEqual(result[1], 404)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

    def test_insufficient_scope(self):
        """ test request_not_found"""
        result = insufficient_scope(None, "some message", "some details")

        self.assertEqual(result[1], 403)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

    def test_unprocessable_entity(self):
        """ test unprocessable_entity"""
        result = unprocessable_entity(None, "some message", "some details")

        self.assertEqual(result[1], 422)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

    def test_method_not_allowed(self):
        """ test unprocessable_entity"""
        result = method_not_allowed(None, "some message", "some details")

        self.assertEqual(result[1], 405)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

    def test_internal_erro(self):
        """ test internal_error """
        result = internal_error("test", "some message", "some details")

        self.assertEqual(result[1], 500)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

    def test_bad_gateway(self):
        """ test bad_gateway"""
        result = bad_gateway("test", "some message", "some details")

        self.assertEqual(result[1], 502)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])

    def test_service_unavailable(self):
        """ test service_unavailable"""
        result = service_unavailable("test", "some message", "some details")

        self.assertEqual(result[1], 503)
        self.assertTrue(result[0]["error"])
        self.assertTrue(result[0]["message"])
        self.assertTrue(result[0]["details"])
