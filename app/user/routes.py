from flask import request, jsonify

from app                import jwt
from app.user           import bp
from app.user.modules   import user
from app.serializer     import UserSchema
from app.errors         import bad_request, internal_error, request_not_found

@bp.route('/register', methods=["POST"])
def user_register_routes():
    # parse request data 
    request_data = request.form
    data = {
        "username"   : request_data["username"],
        "name"       : request_data["name"    ],
        "msisdn"     : request_data["msisdn"  ],
        "email"      : request_data["email"   ],
        "password"   : request_data["password"],
        "pin"        : request_data["pin"     ],
        "role"       : request_data["role"    ],
    }

    # request data validator
    user_obj, errors = UserSchema().load(data)
    if errors:
        return jsonify(bad_request(errors))
    #end if

    response = user.UserController().user_register(data)

    return jsonify(response)
#end def

@bp.route('/list', methods=["GET"])
def user_list_routes():
    response = {
        "status_code"    : 0,
        "status_message" : "SUCCESS",
        "data" : "NONE"
    }

    page = request.args.get("page")

    response = user.UserController().user_list(page)

    return jsonify(response)
#end def

@bp.route('/info/<id>', methods=["GET", "PUT", "DELETE"])
def user_crud_routes(id):
    data = {
        "user_id": id
    }

    if request.method == "GET":
        response = user.UserController().user_info(data)
    elif request.method == "DELETE":
        response = user.UserController().remove_user(data)
    elif request.method == "PUT":
        request_data = request.form
        data = {
            "user_id"    : id,
            "name"       : request_data["name"    ],
            "msisdn"     : request_data["msisdn"  ],
            "email"      : request_data["email"   ],
        }
        # request data validator
        errors = UserSchema().validate(data, partial=("username","password"))
        if errors:
            return jsonify(bad_request(errors))
        #end if

        response = user.UserController().update_user(data)

    return jsonify(response)
#end def
