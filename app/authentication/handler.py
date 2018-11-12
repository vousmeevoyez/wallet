from app                import auth
from app.models         import User
from app.errors         import bad_request, internal_error, request_not_found

@auth.verify_password
def check_password(username):
    user = User.query.filter_by(username=username).first()
    if user:
    return None
#end def
