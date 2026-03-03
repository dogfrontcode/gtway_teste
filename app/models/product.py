"""
Product model - represents a product/service that can be charged.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from app.extensions import db


class Product(db.Model):
    """
    Product represents a product/service that a tenant can sell.
    Can be linked to transactions for easier charge creation.
    """
    __tablename__ = 'products'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Product Information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(100), index=True)
    
    # Pricing
    price = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='BRL', nullable=False)
    
    # Additional Information
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    extra_data = db.Column(JSON, default=dict)
    
    # Stock Management (optional)
    stock_quantity = db.Column(db.Integer)
    track_stock = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Product {self.name} - {self.price} {self.currency}>'
    
    def to_dict(self):
        """Convert product to dictionary."""
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'name': self.name,
            'description': self.description,
            'sku': self.sku,
            'price': f"{float(self.price):.2f}" if self.price else "0.00",
            'currency': self.currency,
            'image_url': self.image_url,
            'category': self.category,
            'extra_data': self.extra_data or {},
            'stock_quantity': self.stock_quantity,
            'track_stock': self.track_stock,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def has_stock(self, quantity: int = 1) -> bool:
        """Check if product has sufficient stock."""
        if not self.track_stock:
            return True
        
        if self.stock_quantity is None:
            return True
        
        return self.stock_quantity >= quantity
    
    def decrease_stock(self, quantity: int = 1):
        """Decrease stock quantity."""
        if self.track_stock and self.stock_quantity is not None:
            self.stock_quantity -= quantity
