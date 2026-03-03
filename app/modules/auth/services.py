"""
Authentication service layer.
"""
from datetime import datetime
from typing import Dict, Tuple, Optional
import uuid
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.models import User, Tenant


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def login(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Authenticate user and generate tokens.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (user_data with tokens, error_message)
        """
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return None, "Invalid email or password"
        
        if not user.check_password(password):
            return None, "Invalid email or password"
        
        if not user.is_active:
            return None, "Account is inactive"
        
        # Check if tenant is active (if user belongs to a tenant)
        if user.tenant_id:
            tenant = Tenant.query.get(user.tenant_id)
            if not tenant or not tenant.is_active:
                return None, "Tenant account is inactive"
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate tokens (use user_id string for compatibility with JWT decoding)
        identity = str(user.id)
        
        additional_claims = {
            'email': user.email,
            'role': user.role,
            'tenant_id': str(user.tenant_id) if user.tenant_id else None
        }
        
        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=identity, additional_claims=additional_claims)
        
        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, None
    
    @staticmethod
    def register(
        email: str,
        password: str,
        full_name: str,
        role: str = 'tenant_user',
        tenant_id: Optional[uuid.UUID] = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user.
        
        Args:
            email: User email
            password: User password
            full_name: User full name
            role: User role
            tenant_id: Tenant ID (required for non-admin users)
            
        Returns:
            Tuple of (user, error_message)
        """
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return None, "Email already registered"
        
        # Validate tenant requirement
        if role != 'admin' and not tenant_id:
            return None, "Tenant ID is required for non-admin users"
        
        # Verify tenant exists and is active
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                return None, "Tenant not found"
            if not tenant.is_active:
                return None, "Tenant is inactive"
        
        # Create user
        user = User(
            email=email,
            full_name=full_name,
            role=role,
            tenant_id=tenant_id
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f"Registration failed: {str(e)}"
    
    @staticmethod
    def refresh_access_token(user_id: str, additional_claims: Dict) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            user_id: User ID string
            additional_claims: Claims from JWT (role, tenant_id, email)
            
        Returns:
            New access token
        """
        return create_access_token(identity=user_id, additional_claims=additional_claims)
    
    @staticmethod
    def get_user_by_id(user_id) -> Optional[User]:
        """Get user by ID (accepts UUID or string)."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        return User.query.get(user_id)
    
    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Change user password.
        
        Args:
            user: User instance
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, error_message)
        """
        if not user.check_password(old_password):
            return False, "Current password is incorrect"
        
        user.set_password(new_password)
        
        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Password change failed: {str(e)}"
