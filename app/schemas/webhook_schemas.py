"""
Webhook-related schemas.
"""
from marshmallow import Schema, fields, validate


class WebhookPayloadSchema(Schema):
    """Schema for webhook payload sent to tenants."""
    transaction_id = fields.UUID(required=True)
    txid = fields.Str(required=True)
    amount = fields.Decimal(required=True, places=2, as_string=True)
    currency = fields.Str(required=True)
    status = fields.Str(required=True)
    description = fields.Str()
    payer_name = fields.Str()
    payer_document = fields.Str()
    paid_at = fields.DateTime()
    created_at = fields.DateTime(required=True)


class BankWebhookSchema(Schema):
    """Schema for incoming webhook from bank/PSP (example - adjust per provider)."""
    txid = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(['paid', 'cancelled', 'expired']))
    amount = fields.Decimal(places=2)
    payer = fields.Dict()
    paid_at = fields.DateTime()
    # Signature/authentication fields
    signature = fields.Str()
    timestamp = fields.DateTime()
