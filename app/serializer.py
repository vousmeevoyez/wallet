from app         import ma
from app.models  import ApiKey

from marshmallow import fields, ValidationError, post_load

def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')

class ApiKeySchema(ma.Schema):
    label = fields.String(validate=must_not_be_blank)
    name  = fields.String(validate=must_not_be_blank)
    id    = fields.Integer()
    access_key = fields.String()
    expiration = fields.DateTime()

    @post_load
    def make_api_key(self, data):
        return ApiKey(**data)

class WalletSchema(ma.Schema):
    id        = fields.Integer()
    name      = fields.String(validate=must_not_be_blank)
    wallet_id = fields.Integer(validate=must_not_be_blank)
    msisdn    = fields.Integer(validate=must_not_be_blank)
    email     = fields.String(validate=must_not_be_blank)
    create_at = fields.DateTime()
    pin_hash  = fields.String(validate=must_not_be_blank)
    status    = fields.Boolean()
    balance   = fields.Integer()

    @post_load
    def make_wallet(self, data):
        return Wallet(**data)


