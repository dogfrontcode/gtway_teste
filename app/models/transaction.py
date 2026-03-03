"""
Transaction model - represents a payment transaction/charge.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from app.extensions import db


class Transaction(db.Model):
    """
    Transaction represents a payment charge (typically PIX).
    """
    __tablename__ = 'transactions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False, index=True)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=True, index=True)
    
    # Transaction Identifiers
    txid = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Bank transaction ID
    external_id = db.Column(db.String(100), index=True)  # Optional ID from tenant's system
    
    # Payment Details
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # Amount in BRL (or other currency)
    currency = db.Column(db.String(3), default='BRL', nullable=False)
    description = db.Column(db.Text)
    
    # PIX Details
    pix_key = db.Column(db.String(255))  # PIX key used for this transaction
    qr_code = db.Column(db.Text)  # QR Code (base64 image or URL)
    qr_code_text = db.Column(db.Text)  # QR Code "copia e cola" text
    
    # Payer Information (optional, if provided by bank)
    payer_name = db.Column(db.String(200))
    payer_document = db.Column(db.String(20))  # CPF/CNPJ
    
    # Status: 'pending', 'paid', 'expired', 'cancelled', 'refunded'
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    
    # Bank Response (store full response for debugging)
    bank_response = db.Column(JSON)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, index=True)  # When the charge expires
    paid_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    webhook_attempts = db.relationship('WebhookAttempt', backref='transaction', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Transaction {self.txid} - {self.status} - {self.amount} {self.currency}>'
    
    def to_dict(self, include_sensitive=False):
        """Convert transaction to dictionary."""
        data = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'txid': self.txid,
            'external_id': self.external_id,
            'amount': f"{float(self.amount):.2f}" if self.amount else "0.00",
            'currency': self.currency,
            'description': self.description,
            'status': self.status,
            'payer_name': self.payer_name,
            'payer_document': self.payer_document,
            'created_at': self.created_at.isoformat() if self.created_at and hasattr(self.created_at, 'isoformat') else self.created_at,
            'expires_at': self.expires_at.isoformat() if self.expires_at and hasattr(self.expires_at, 'isoformat') else self.expires_at,
            'paid_at': self.paid_at.isoformat() if self.paid_at and hasattr(self.paid_at, 'isoformat') else self.paid_at,
            'updated_at': self.updated_at.isoformat() if self.updated_at and hasattr(self.updated_at, 'isoformat') else self.updated_at,
        }
        
        if include_sensitive:
            data['qr_code'] = self.qr_code
            data['qr_code_text'] = self.qr_code_text
            data['pix_key'] = self.pix_key
            data['bank_response'] = self.bank_response
        
        return data
    
    def is_paid(self) -> bool:
        """Check if transaction is paid."""
        return self.status == 'paid'
    
    def is_pending(self) -> bool:
        """Check if transaction is pending payment."""
        return self.status == 'pending'
    
    def mark_as_paid(self, paid_at: datetime = None, payer_info: dict = None):
        """Mark transaction as paid."""
        self.status = 'paid'
        self.paid_at = paid_at or datetime.utcnow()
        
        if payer_info:
            self.payer_name = payer_info.get('name')
            self.payer_document = payer_info.get('document')
    
    @staticmethod
    def generate_txid(prefix: str = 'TXN') -> str:
        """Generate a unique transaction ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"{prefix}{timestamp}{unique_id}"
