"""
    Core Module
"""
from flask import request
from flask_restplus import Resource  # pylint: disable=import-error

from marshmallow import ValidationError

from app.lib.http_error import BadRequest

from app.api.const import ERROR as error_response


class CoreRoutes:
    """ base routes class"""

    __schema__ = None
    __serializer__ = None

    def _validate(self, payload):
        """ validate incoming request payload, preprocess it and then return
        the validated result
        :param payload: incoming HTTP Request Body
        """
        # preprocess everything here
        payload = self.preprocess(payload)

        if self.__serializer__ is not None:
            try:
                serialized = self.__serializer__.validate(payload)
            except ValidationError as error:
                raise BadRequest(
                    error_response["INVALID_PARAMETER"]["TITLE"],
                    error_response["INVALID_PARAMETER"]["MESSAGE"],
                    error.messages,
                )
            # end try
        # end if
        return payload

    # end def

    def _load(self, payload):
        """ validate incoming request payload, preprocess it and then load it
        into object
        :param payload: incoming HTTP Request Body
        """
        # preprocess everything here
        payload = self.preprocess(payload)

        try:
            serialized = self.__serializer__.load(payload)
        except ValidationError as error:
            raise BadRequest(
                error_response["INVALID_PARAMETER"]["TITLE"],
                error_response["INVALID_PARAMETER"]["MESSAGE"],
                error.messages,
            )
        # end if
        return serialized.data

    # end def

    def preprocess(self, payload):
        """ preprocess incoming request payload
        can be overriden by subclass
        :param payload: incoming HTTP Request Body
        """
        return payload

    def payload(self, raw=False):
        """ interface to help HTTP Request body either via Restful Reqparse or
        Flask
        :param raw: if its True it mean accessing Raw via Flask Request
        """
        payload = request.get_json()
        if raw is False:
            payload = self.__schema__.parser.parse_args(strict=True)
        # end if
        return payload

    # end def

    def serialize(self, payload, load=False):
        """ interface to serialize incoming Request Payload and decide whether
        only validate or load it into an object
        :param payload: if its True it mean accessing Raw via Flask Request
        :param load : True load request payload into object
        """
        result = self._validate(payload)
        if load:
            result = self._load(payload)
        return result

    # end def


# end class


class Routes(CoreRoutes, Resource):
    pass
