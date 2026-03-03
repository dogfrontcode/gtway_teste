"""
WebhookAttempt model - tracks webhook delivery attempts to tenants.
"""
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from app.extensions import db


class WebhookAttempt(db.Model):
    """
    WebhookAttempt tracks each attempt to deliver a webhook notification to a tenant.
    Used for retry logic and audit trail.
    """
    __tablename__ = 'webhook_attempts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = db.Column(UUID(as_uuid=True), db.ForeignKey('transactions.id'), nullable=False, index=True)
    
    # Attempt Details
    attempt_number = db.Column(db.Integer, nullable=False, default=1)
    url = db.Column(db.String(500), nullable=False)
    
    # Request & Response
    payload = db.Column(JSON)  # The data sent
    response_status = db.Column(db.Integer)  # HTTP status code
    response_body = db.Column(db.Text)  # Response from tenant's webhook
    error_message = db.Column(db.Text)  # Error message if request failed
    
    # Status: 'pending', 'success', 'failed'
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    attempted_at = db.Column(db.DateTime)
    next_retry_at = db.Column(db.DateTime, index=True)  # When to retry if failed
    
    def __repr__(self):
        return f'<WebhookAttempt {self.id} - Attempt {self.attempt_number} - {self.status}>'
    
    def to_dict(self):
        """Convert webhook attempt to dictionary."""
        return {
            'id': str(self.id),
            'transaction_id': str(self.transaction_id),
            'attempt_number': self.attempt_number,
            'url': self.url,
            'payload': self.payload,
            'response_status': self.response_status,
            'response_body': self.response_body,
            'error_message': self.error_message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at and hasattr(self.created_at, 'isoformat') else self.created_at,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at and hasattr(self.attempted_at, 'isoformat') else self.attempted_at,
            'next_retry_at': self.next_retry_at.isoformat() if self.next_retry_at and hasattr(self.next_retry_at, 'isoformat') else self.next_retry_at,
        }
    
    def mark_success(self, response_status: int, response_body: str = None):
        """Mark attempt as successful."""
        self.status = 'success'
        self.response_status = response_status
        self.response_body = response_body
        self.attempted_at = datetime.utcnow()
    
    def mark_failed(self, error_message: str, response_status: int = None, response_body: str = None):
        """Mark attempt as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.response_status = response_status
        self.response_body = response_body
        self.attempted_at = datetime.utcnow()
