"""
Transaction-related schemas.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from decimal import Decimal


class TransactionCreateSchema(Schema):
    """Schema for creating a transaction/charge."""
    amount = fields.Decimal(required=True, places=2, as_string=False)
    currency = fields.Str(validate=validate.OneOf(['BRL', 'USD', 'EUR']), missing='BRL')
    description = fields.Str(validate=validate.Length(max=500))
    external_id = fields.Str(validate=validate.Length(max=100))
    expires_in_minutes = fields.Int(validate=validate.Range(min=5, max=1440), missing=60)
    
    @validates('amount')
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError('Amount must be greater than zero')
        if value > Decimal('999999.99'):
            raise ValidationError('Amount exceeds maximum limit')


class TransactionResponseSchema(Schema):
    """Schema for transaction response."""
    id = fields.UUID(dump_only=True)
    tenant_id = fields.UUID(dump_only=True)
    txid = fields.Str()
    external_id = fields.Str()
    amount = fields.Decimal(places=2, as_string=True)
    currency = fields.Str()
    description = fields.Str()
    status = fields.Str()
    payer_name = fields.Str()
    payer_document = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    expires_at = fields.DateTime()
    paid_at = fields.DateTime()
    updated_at = fields.DateTime(dump_only=True)
    # Sensitive fields
    qr_code = fields.Str(dump_only=True)
    qr_code_text = fields.Str(dump_only=True)
    pix_key = fields.Str(dump_only=True)


class TransactionListSchema(Schema):
    """Schema for transaction list filters."""
    status = fields.Str(validate=validate.OneOf(['pending', 'paid', 'expired', 'cancelled', 'refunded']))
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=20)


class TransactionStatusUpdateSchema(Schema):
    """Schema for updating transaction status (internal use)."""
    status = fields.Str(
        required=True,
        validate=validate.OneOf(['pending', 'paid', 'expired', 'cancelled', 'refunded'])
    )
    payer_name = fields.Str(validate=validate.Length(max=200))
    payer_document = fields.Str(validate=validate.Length(max=20))
    paid_at = fields.DateTime()
