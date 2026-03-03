"""
User model - represents users who access the system (tenant staff or admins).
"""
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """
    User model for authentication and authorization.
    Can be a global admin or a tenant-specific user.
    """
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=True, index=True)
    
    # User Information
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    
    # Role: 'admin' (global), 'tenant_admin', 'tenant_user'
    role = db.Column(db.String(50), nullable=False, default='tenant_user')
    
    # Status & Timestamps
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
    
    def set_password(self, password: str):
        """Hash and set the user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """Check if user is a global admin."""
        return self.role == 'admin'
    
    def is_tenant_admin(self) -> bool:
        """Check if user is a tenant admin."""
        return self.role == 'tenant_admin'
    
    def can_manage_tenant(self, tenant_id: uuid.UUID) -> bool:
        """Check if user can manage a specific tenant."""
        if self.is_admin():
            return True
        return str(self.tenant_id) == str(tenant_id) and self.is_tenant_admin()
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id) if self.tenant_id else None,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login and hasattr(self.last_login, 'isoformat') else self.last_login,
            'created_at': self.created_at.isoformat() if self.created_at and hasattr(self.created_at, 'isoformat') else self.created_at,
            'updated_at': self.updated_at.isoformat() if self.updated_at and hasattr(self.updated_at, 'isoformat') else self.updated_at,
        }
