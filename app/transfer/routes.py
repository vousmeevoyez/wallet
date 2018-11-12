import traceback

from flask import request, jsonify

from app.transfer           import bp
from app.serializer         import TransactionSchema
from app.transfer.modules   import transfer

@bp.route('/direct', methods=["POST"])
def virtual_transfer():
    # parse request data 
    request_data = request.form
    data = {
        "source"      : request_data["source"],
        "destination" : request_data["destination"],
        "amount"      : request_data["amount"],
        "notes"       : request_data["notes"],
        "pin"         : request_data["pin"],
    }

    # request data validator
    errors = TransactionSchema().validate(data)
    if errors:
        return jsonify(bad_request(errors))

    response = transfer.TransferController().internal_transfer(data)

    return jsonify(response)
#end def
