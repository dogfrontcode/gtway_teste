"""
Product schemas for validation and serialization.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from decimal import Decimal


class ProductCreateSchema(Schema):
    """Schema for creating a product."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    sku = fields.Str(allow_none=True, validate=validate.Length(max=100))
    price = fields.Decimal(required=True, as_string=False, places=2)
    currency = fields.Str(missing='BRL', validate=validate.Length(equal=3))
    image_url = fields.Url(allow_none=True)
    category = fields.Str(allow_none=True, validate=validate.Length(max=100))
    extra_data = fields.Dict(missing=dict)
    stock_quantity = fields.Int(allow_none=True, validate=validate.Range(min=0))
    track_stock = fields.Bool(missing=False)
    is_active = fields.Bool(missing=True)
    
    @validates('price')
    def validate_price(self, value):
        """Validate that price is positive."""
        if value <= 0:
            raise ValidationError('Price must be greater than 0')


class ProductUpdateSchema(Schema):
    """Schema for updating a product."""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    sku = fields.Str(allow_none=True, validate=validate.Length(max=100))
    price = fields.Decimal(as_string=False, places=2)
    currency = fields.Str(validate=validate.Length(equal=3))
    image_url = fields.Url(allow_none=True)
    category = fields.Str(allow_none=True, validate=validate.Length(max=100))
    extra_data = fields.Dict()
    stock_quantity = fields.Int(allow_none=True, validate=validate.Range(min=0))
    track_stock = fields.Bool()
    is_active = fields.Bool()
    
    @validates('price')
    def validate_price(self, value):
        """Validate that price is positive."""
        if value and value <= 0:
            raise ValidationError('Price must be greater than 0')
