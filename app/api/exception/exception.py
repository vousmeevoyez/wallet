from werkzeug.exceptions import MethodNotAllowed, BadRequest, HTTPException, NotFound

from app.api.exception import api
from app.api.errors    import error_response

@api.errorhandler(BadRequest)
def bad_request_custom_handler(error):
    error_code = getattr(error, "code")
    return error_response( error_code, str(error))
