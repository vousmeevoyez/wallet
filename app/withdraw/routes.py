import traceback
from flask          import request, jsonify

from app.withdraw           import bp
from app.serializer         import WalletSchema
from app.errors             import bad_request, internal_error, request_not_found
from app.config             import config
from app.withdraw.modules   import withdraw

@bp.route('/request', methods=["POST"])
def wtihdraw_wallet():
    request_data = request.form
    data = {
        "wallet_id" : request_data["wallet_id" ],
        "pin"       : request_data["pin"       ],
        "amount"    : request_data["amount"    ],
    }

    response = withdraw.WithdrawController().request(data)
    return jsonify(response)
#end def
