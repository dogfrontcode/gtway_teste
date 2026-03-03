"""
Tenant model - represents a company using the gateway.
"""
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from app.extensions import db


class Tenant(db.Model):
    """
    Tenant represents a company/merchant using the payment gateway.
    Each tenant has isolated data and custom configurations.
    """
    __tablename__ = 'tenants'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Company Information
    name = db.Column(db.String(200), nullable=False)
    legal_name = db.Column(db.String(200))
    cnpj = db.Column(db.String(18), unique=True, index=True)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    
    # White Label Settings (stored as JSON)
    settings = db.Column(JSON, default=dict)  # colors, logo_url, custom_domain, etc.
    
    # Payment Configuration
    bank_provider = db.Column(db.String(50), default='mock')  # mock, bradesco, openPix, etc.
    pix_key = db.Column(db.String(255))
    bank_credentials = db.Column(db.Text)  # Encrypted JSON with bank API credentials
    
    # Webhook Configuration
    webhook_url = db.Column(db.String(500))  # URL to send notifications to tenant
    webhook_secret = db.Column(db.String(255))  # Secret for validating webhooks to tenant
    
    # API Access
    api_key = db.Column(db.String(100), unique=True, index=True)
    
    # Status & Timestamps
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = db.relationship('User', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.name} ({self.slug})>'
    
    def to_dict(self, include_sensitive=False):
        """Convert tenant to dictionary."""
        data = {
            'id': str(self.id),
            'slug': self.slug,
            'name': self.name,
            'legal_name': self.legal_name,
            'cnpj': self.cnpj,
            'email': self.email,
            'phone': self.phone,
            'settings': self.settings or {},
            'bank_provider': self.bank_provider,
            'pix_key': self.pix_key,
            'webhook_url': self.webhook_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at and hasattr(self.created_at, 'isoformat') else self.created_at,
            'updated_at': self.updated_at.isoformat() if self.updated_at and hasattr(self.updated_at, 'isoformat') else self.updated_at,
        }
        
        if include_sensitive:
            data['api_key'] = self.api_key
            data['webhook_secret'] = self.webhook_secret
        
        return data
    
    @staticmethod
    def generate_api_key():
        """Generate a unique API key for tenant authentication."""
        return f"sk_live_{uuid.uuid4().hex}"
