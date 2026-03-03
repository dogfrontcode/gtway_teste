"""
Authentication-related schemas.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from app.utils.validators import validate_email


class LoginSchema(Schema):
    """Schema for user login."""
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))


class RegisterSchema(Schema):
    """Schema for user registration."""
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    role = fields.Str(
        validate=validate.OneOf(['admin', 'tenant_admin', 'tenant_user']),
        missing='tenant_user'
    )
    tenant_id = fields.UUID(allow_none=True)
    
    @validates('email')
    def validate_email_format(self, value):
        if not validate_email(value):
            raise ValidationError('Invalid email format')


class TokenRefreshSchema(Schema):
    """Schema for token refresh."""
    refresh_token = fields.Str(required=True)


class PasswordChangeSchema(Schema):
    """Schema for password change."""
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=100))
