from flask              import request
from flask_restplus     import Resource

from app.api                import db
from app.api.user           import api
from app.api.serializer     import UserSchema
from app.api.request_schema import UserRequestSchema

from app.api.authentication.decorator import token_required, admin_required

from app.api.user.modules   import user

from app.api.errors import bad_request, internal_error, request_not_found

user_request_schema = UserRequestSchema.parser

@api.route("/")
class UserRoutes(Resource):
    @admin_required
    def post(self):
        request_data = user_request_schema.parse_args(strict=True)
        data = {
            "username"    : request_data["username"    ],
            "name"        : request_data["name"        ],
            "phone_ext"   : request_data["phone_ext"   ],
            "phone_number": request_data["phone_number"],
            "email"       : request_data["email"       ],
            "password"    : request_data["password"    ],
            "pin"         : request_data["pin"         ],
            "role"        : request_data["role"        ],
        }

        # request data validator
        errors = UserSchema().validate(data)
        if errors:
            return bad_request(errors)
        #end if

        response = user.UserController().user_register(data)
        return response
    #end def

    @admin_required
    def get(self):
        response = user.UserController().user_list(1)
        return response
#end class

@api.route("/<int:user_id>")
class UserInfoRoutes(Resource):
    @token_required
    def get(self, user_id):
        response = user.UserController().user_info({ "user_id" : user_id })
        return response
    #end def
#end class
