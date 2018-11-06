import traceback

from flask          import request, jsonify
from marshmallow    import ValidationError, pprint
from sqlalchemy.exc import IntegrityError

from app            import db
from app.access_key import bp
from app.models     import ApiKey
from app.serializer import ApiKeySchema
from app.errors     import bad_request, internal_error
from app.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG

class AccessKeyController:

    def __init__(self):
        pass
    #end def

    def create_access_key(self, obj):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            obj.generate_access_key(ACCESS_KEY_CONFIG["TOKEN_LENGTH"])
            obj.set_expiration(ACCESS_KEY_CONFIG["EXPIRE_IN"])

            db.session.add(obj)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return bad_request("Error adding record")
        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        response["data"] = "Secret key successfully created"


        return response
    #end def

    def list_access_key(self, page):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            query_result = ApiKey.query.all()
            result, errors = ApiKeySchema(many=True).dump(query_result)

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        response["data"] = result

        return response
    #end def

    def revoke_access_key(self, id):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            result = ApiKey.query.filter_by(access_key=id).first()
            if result is None:
                return bad_request("Item not found")
            #end if
            result.revoke_access_key()
            db.session.commit()

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        response["data"] = "Key revoked"

        return response
    #end def

    def check_access_key(self, id):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            access_key_status = ApiKey.check_access_key(id)

            if access_key_status is None:
                return bad_request("INVALID TOKEN")
            #end if

            result.errors = ApiKeySchema().dump(access_key_status).data
            if errors:
                return bad_request(errors)
            #end if

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        response["data"] = result

        return response
    #end def

    def remove_access_key(self, id):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            result = ApiKey.query.filter_by(access_key=id).first()

            if result is None:
                return bad_request("Item not found")
            #end if

            db.session.delete(result)
            db.session.commit()

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        response["data"] = result

        return response
    #end def

#end class
