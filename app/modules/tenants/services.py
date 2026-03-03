"""
Tenant service layer.
"""
import uuid
from typing import Dict, List, Optional, Tuple
from flask import current_app
from app.extensions import db
from app.models import Tenant, User
from app.utils.security import encrypt_data, decrypt_data
from app.utils.validators import sanitize_slug
from app.utils.cnpj_validator import validate_cnpj


class TenantService:
    """Service for tenant operations."""
    
    @staticmethod
    def create_tenant(data: Dict) -> Tuple[Optional[Tenant], Optional[str]]:
        """
        Create a new tenant.
        
        Args:
            data: Tenant data
            
        Returns:
            Tuple of (tenant, error_message)
        """
        try:
            # Check if slug is unique
            slug = data.get('slug') or sanitize_slug(data['name'])
            if Tenant.query.filter_by(slug=slug).first():
                return None, f"Slug '{slug}' is already in use"
            
            # Check if CNPJ is unique (if provided)
            if data.get('cnpj'):
                # Validate CNPJ format
                if not validate_cnpj(data['cnpj']):
                    return None, "Invalid CNPJ format"
                
                if Tenant.query.filter_by(cnpj=data['cnpj']).first():
                    return None, "CNPJ already registered"
            
            # Encrypt bank credentials if provided
            encrypted_credentials = None
            if data.get('bank_credentials'):
                try:
                    encrypted_credentials = encrypt_data(data['bank_credentials'])
                except Exception as e:
                    current_app.logger.error(f"Credential encryption error: {e}")
                    return None, "Failed to encrypt bank credentials"
            
            # Generate API key
            api_key = Tenant.generate_api_key()
            
            # Generate webhook secret if webhook_url provided
            webhook_secret = None
            if data.get('webhook_url'):
                webhook_secret = f"whsec_{uuid.uuid4().hex}"
            
            # Create tenant
            tenant = Tenant(
                slug=slug,
                name=data['name'],
                legal_name=data.get('legal_name'),
                cnpj=data.get('cnpj'),
                email=data['email'],
                phone=data.get('phone'),
                pix_key=data.get('pix_key'),
                bank_provider=data.get('bank_provider', 'mock'),
                bank_credentials=encrypted_credentials,
                webhook_url=data.get('webhook_url'),
                webhook_secret=webhook_secret,
                api_key=api_key,
                settings=data.get('settings', {})
            )
            
            db.session.add(tenant)
            db.session.commit()
            
            # Custom log
            from app.utils.logger import log_success
            log_success(f"Tenant criado: {tenant.slug}")
            
            current_app.logger.info(f"Tenant created: {tenant.slug} ({tenant.id})")
            return tenant, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Tenant creation error: {e}")
            return None, f"Failed to create tenant: {str(e)}"
    
    @staticmethod
    def get_tenant(tenant_id) -> Optional[Tenant]:
        """Get tenant by ID (accepts UUID or string)."""
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        return Tenant.query.get(tenant_id)
    
    @staticmethod
    def get_tenant_by_slug(slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        return Tenant.query.filter_by(slug=slug).first()
    
    @staticmethod
    def get_tenant_by_api_key(api_key: str) -> Optional[Tenant]:
        """Get tenant by API key."""
        return Tenant.query.filter_by(api_key=api_key).first()
    
    @staticmethod
    def list_tenants(
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Tenant], int]:
        """
        List tenants with pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            is_active: Filter by active status
            
        Returns:
            Tuple of (tenants, total_count)
        """
        query = Tenant.query
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        query = query.order_by(Tenant.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def update_tenant(tenant: Tenant, data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Update tenant information.
        
        Args:
            tenant: Tenant instance
            data: Update data
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Update basic fields
            if 'name' in data:
                tenant.name = data['name']
            if 'legal_name' in data:
                tenant.legal_name = data['legal_name']
            if 'email' in data:
                tenant.email = data['email']
            if 'phone' in data:
                tenant.phone = data['phone']
            if 'pix_key' in data:
                tenant.pix_key = data['pix_key']
            if 'bank_provider' in data:
                tenant.bank_provider = data['bank_provider']
            if 'webhook_url' in data:
                tenant.webhook_url = data['webhook_url']
                # Generate webhook secret if not exists
                if not tenant.webhook_secret:
                    tenant.webhook_secret = f"whsec_{uuid.uuid4().hex}"
            if 'webhook_secret' in data:
                tenant.webhook_secret = data['webhook_secret']
            if 'settings' in data:
                tenant.settings = data['settings']
            if 'is_active' in data:
                tenant.is_active = data['is_active']
            
            # Encrypt and update bank credentials if provided
            if 'bank_credentials' in data:
                try:
                    encrypted = encrypt_data(data['bank_credentials'])
                    tenant.bank_credentials = encrypted
                except Exception as e:
                    current_app.logger.error(f"Credential encryption error: {e}")
                    return False, "Failed to encrypt bank credentials"
            
            db.session.commit()
            
            current_app.logger.info(f"Tenant updated: {tenant.slug} ({tenant.id})")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Tenant update error: {e}")
            return False, f"Failed to update tenant: {str(e)}"
    
    @staticmethod
    def delete_tenant(tenant: Tenant) -> Tuple[bool, Optional[str]]:
        """
        Delete tenant (soft delete by marking as inactive).
        
        Args:
            tenant: Tenant instance
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            tenant.is_active = False
            db.session.commit()
            
            current_app.logger.info(f"Tenant deactivated: {tenant.slug} ({tenant.id})")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Tenant deletion error: {e}")
            return False, f"Failed to delete tenant: {str(e)}"
    
    @staticmethod
    def get_tenant_credentials(tenant: Tenant) -> Optional[Dict]:
        """
        Get decrypted bank credentials for a tenant.
        
        Args:
            tenant: Tenant instance
            
        Returns:
            Decrypted credentials or None
        """
        if not tenant.bank_credentials:
            return None
        
        try:
            return decrypt_data(tenant.bank_credentials)
        except Exception as e:
            current_app.logger.error(f"Credential decryption error: {e}")
            return None
    
    @staticmethod
    def regenerate_api_key(tenant: Tenant) -> Tuple[Optional[str], Optional[str]]:
        """
        Regenerate API key for tenant.
        
        Args:
            tenant: Tenant instance
            
        Returns:
            Tuple of (new_api_key, error_message)
        """
        try:
            new_api_key = Tenant.generate_api_key()
            tenant.api_key = new_api_key
            db.session.commit()
            
            current_app.logger.info(f"API key regenerated for tenant: {tenant.slug}")
            return new_api_key, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"API key regeneration error: {e}")
            return None, f"Failed to regenerate API key: {str(e)}"
