"""
Payment service layer.
"""
import uuid
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from flask import current_app
from app.extensions import db
from app.models import Transaction, Tenant
from app.modules.payments.providers.factory import get_provider
from app.modules.payments.providers.base import ProviderError
from app.modules.tenants.services import TenantService


class PaymentService:
    """Service for payment operations."""
    
    @staticmethod
    def create_charge(
        tenant: Tenant,
        amount: Decimal,
        description: Optional[str] = None,
        external_id: Optional[str] = None,
        expires_in_minutes: int = 60
    ) -> Tuple[Optional[Transaction], Optional[str]]:
        """
        Create a new payment charge.
        
        Args:
            tenant: Tenant instance
            amount: Amount to charge
            description: Payment description
            external_id: External reference ID
            expires_in_minutes: Expiration time
            
        Returns:
            Tuple of (transaction, error_message)
        """
        try:
            # Validate tenant
            if not tenant.is_active:
                return None, "Tenant is inactive"
            
            if not tenant.pix_key:
                return None, "Tenant does not have a PIX key configured"
            
            # Get provider
            credentials = TenantService.get_tenant_credentials(tenant)
            provider = get_provider(tenant.bank_provider, credentials)
            
            # Create charge with provider
            try:
                charge_data = provider.create_charge(
                    amount=amount,
                    pix_key=tenant.pix_key,
                    description=description,
                    external_id=external_id,
                    expires_in_minutes=expires_in_minutes
                )
            except ProviderError as e:
                current_app.logger.error(f"Provider error creating charge: {e.message}")
                return None, f"Payment provider error: {e.message}"
            
            # Create transaction record
            transaction = Transaction(
                tenant_id=tenant.id,
                txid=charge_data['txid'],
                external_id=external_id,
                amount=amount,
                currency='BRL',
                description=description,
                pix_key=tenant.pix_key,
                qr_code=charge_data.get('qr_code'),
                qr_code_text=charge_data.get('qr_code_text'),
                status='pending',
                expires_at=charge_data.get('expires_at'),
                bank_response=charge_data.get('raw_response')
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            current_app.logger.info(
                f"Charge created: {transaction.txid} for tenant {tenant.slug} - "
                f"Amount: {amount}"
            )
            
            return transaction, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Charge creation error: {e}")
            return None, f"Failed to create charge: {str(e)}"
    
    @staticmethod
    def get_transaction(transaction_id: uuid.UUID) -> Optional[Transaction]:
        """Get transaction by ID."""
        return Transaction.query.get(transaction_id)
    
    @staticmethod
    def get_transaction_by_txid(txid: str) -> Optional[Transaction]:
        """Get transaction by txid."""
        return Transaction.query.filter_by(txid=txid).first()
    
    @staticmethod
    def list_transactions(
        tenant: Tenant,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Transaction], int]:
        """
        List transactions for a tenant.
        
        Args:
            tenant: Tenant instance
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (transactions, total_count)
        """
        query = Transaction.query.filter_by(tenant_id=tenant.id)
        
        if status:
            query = query.filter_by(status=status)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        query = query.order_by(Transaction.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def update_transaction_status(
        transaction: Transaction,
        status: str,
        payer_info: Optional[Dict] = None,
        paid_at: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update transaction status.
        
        Args:
            transaction: Transaction instance
            status: New status
            payer_info: Payer information
            paid_at: Payment datetime
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            transaction.status = status
            
            if status == 'paid':
                transaction.mark_as_paid(paid_at, payer_info)
            
            db.session.commit()
            
            current_app.logger.info(
                f"Transaction {transaction.txid} status updated to {status}"
            )
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Transaction update error: {e}")
            return False, f"Failed to update transaction: {str(e)}"
    
    @staticmethod
    def check_charge_status(transaction: Transaction) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Check charge status with payment provider.
        
        Args:
            transaction: Transaction instance
            
        Returns:
            Tuple of (status_data, error_message)
        """
        try:
            tenant = transaction.tenant
            
            # Get provider
            credentials = TenantService.get_tenant_credentials(tenant)
            provider = get_provider(tenant.bank_provider, credentials)
            
            # Check status
            try:
                status_data = provider.get_charge_status(transaction.txid)
                return status_data, None
            except ProviderError as e:
                current_app.logger.error(f"Provider error checking status: {e.message}")
                return None, f"Payment provider error: {e.message}"
            
        except Exception as e:
            current_app.logger.error(f"Status check error: {e}")
            return None, f"Failed to check status: {str(e)}"
    
    @staticmethod
    def cancel_charge(transaction: Transaction) -> Tuple[bool, Optional[str]]:
        """
        Cancel a pending charge.
        
        Args:
            transaction: Transaction instance
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if transaction.status != 'pending':
                return False, "Only pending transactions can be cancelled"
            
            tenant = transaction.tenant
            
            # Get provider
            credentials = TenantService.get_tenant_credentials(tenant)
            provider = get_provider(tenant.bank_provider, credentials)
            
            # Cancel with provider
            try:
                provider.cancel_charge(transaction.txid)
            except ProviderError as e:
                current_app.logger.error(f"Provider error cancelling charge: {e.message}")
                return False, f"Payment provider error: {e.message}"
            
            # Update transaction status
            transaction.status = 'cancelled'
            db.session.commit()
            
            current_app.logger.info(f"Charge cancelled: {transaction.txid}")
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Charge cancellation error: {e}")
            return False, f"Failed to cancel charge: {str(e)}"
    
    @staticmethod
    def get_payment_statistics(tenant: Tenant, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """
        Get payment statistics for a tenant.
        
        Args:
            tenant: Tenant instance
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dict with statistics
        """
        query = Transaction.query.filter_by(tenant_id=tenant.id)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        transactions = query.all()
        
        total_amount = sum(t.amount for t in transactions if t.status == 'paid')
        total_transactions = len(transactions)
        paid_transactions = len([t for t in transactions if t.status == 'paid'])
        pending_transactions = len([t for t in transactions if t.status == 'pending'])
        
        return {
            'total_amount': float(total_amount),
            'total_transactions': total_transactions,
            'paid_transactions': paid_transactions,
            'pending_transactions': pending_transactions,
            'conversion_rate': (paid_transactions / total_transactions * 100) if total_transactions > 0 else 0
        }
