"""
Tenant-related schemas.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load
from app.utils.validators import validate_cnpj, validate_pix_key, sanitize_slug


class TenantCreateSchema(Schema):
    """Schema for creating a tenant."""
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    slug = fields.Str(validate=validate.Length(min=2, max=100))
    legal_name = fields.Str(validate=validate.Length(max=200))
    cnpj = fields.Str(validate=validate.Length(max=18))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    phone = fields.Str(validate=validate.Length(max=20))
    pix_key = fields.Str(validate=validate.Length(max=255))
    bank_provider = fields.Str(
        validate=validate.OneOf(['mock', 'bradesco', 'openPix', 'inter']),
        missing='mock'
    )
    bank_credentials = fields.Dict()  # Will be encrypted
    webhook_url = fields.Url(validate=validate.Length(max=500))
    settings = fields.Dict(missing=dict)
    
    @pre_load
    def generate_slug(self, data, **kwargs):
        """Auto-generate slug from name if not provided."""
        if 'slug' not in data or not data['slug']:
            data['slug'] = sanitize_slug(data.get('name', ''))
        return data
    
    @validates('cnpj')
    def validate_cnpj_format(self, value):
        if value and not validate_cnpj(value):
            raise ValidationError('Invalid CNPJ format')
    
    @validates('pix_key')
    def validate_pix_key_format(self, value):
        if value and not validate_pix_key(value):
            raise ValidationError('Invalid PIX key format')


class TenantUpdateSchema(Schema):
    """Schema for updating a tenant."""
    name = fields.Str(validate=validate.Length(min=2, max=200))
    legal_name = fields.Str(validate=validate.Length(max=200))
    email = fields.Email(validate=validate.Length(max=120))
    phone = fields.Str(validate=validate.Length(max=20))
    pix_key = fields.Str(validate=validate.Length(max=255))
    bank_provider = fields.Str(
        validate=validate.OneOf(['mock', 'bradesco', 'openPix', 'inter'])
    )
    bank_credentials = fields.Dict()
    webhook_url = fields.Url(validate=validate.Length(max=500))
    webhook_secret = fields.Str(validate=validate.Length(max=255))
    settings = fields.Dict()
    is_active = fields.Bool()
    
    @validates('pix_key')
    def validate_pix_key_format(self, value):
        if value and not validate_pix_key(value):
            raise ValidationError('Invalid PIX key format')


class TenantResponseSchema(Schema):
    """Schema for tenant response."""
    id = fields.UUID(dump_only=True)
    slug = fields.Str()
    name = fields.Str()
    legal_name = fields.Str()
    cnpj = fields.Str()
    email = fields.Email()
    phone = fields.Str()
    bank_provider = fields.Str()
    pix_key = fields.Str()
    webhook_url = fields.Str()
    settings = fields.Dict()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    # Sensitive fields only included when requested
    api_key = fields.Str(dump_only=True)
    webhook_secret = fields.Str(dump_only=True)
