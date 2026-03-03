"""
Webhook service layer.
"""
from typing import Dict, Optional, Tuple
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models import Transaction
from app.modules.payments.services import PaymentService
from app.modules.webhooks.tasks import send_tenant_webhook


class WebhookService:
    """Service for webhook operations."""
    
    @staticmethod
    def process_bank_webhook(
        txid: str,
        status: str,
        amount: Optional[float] = None,
        payer_info: Optional[Dict] = None,
        paid_at: Optional[datetime] = None,
        signature: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Process incoming webhook from bank/PSP.
        
        Args:
            txid: Transaction ID
            status: New status
            amount: Payment amount (for verification)
            payer_info: Payer information
            paid_at: Payment datetime
            signature: Webhook signature (for validation)
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Find transaction
            transaction = PaymentService.get_transaction_by_txid(txid)
            
            if not transaction:
                current_app.logger.warning(f"Transaction not found for txid: {txid}")
                return False, "Transaction not found"
            
            # Validate amount if provided
            if amount and float(transaction.amount) != float(amount):
                current_app.logger.error(
                    f"Amount mismatch for {txid}: expected {transaction.amount}, got {amount}"
                )
                return False, "Amount mismatch"
            
            # Don't process if already in final state
            if transaction.status in ('paid', 'refunded', 'cancelled'):
                current_app.logger.info(
                    f"Transaction {txid} already in final state: {transaction.status}"
                )
                return True, None
            
            # Update transaction status
            old_status = transaction.status
            success, error = PaymentService.update_transaction_status(
                transaction=transaction,
                status=status,
                payer_info=payer_info,
                paid_at=paid_at or datetime.utcnow()
            )
            
            if not success:
                return False, error
            
            current_app.logger.info(
                f"Transaction {txid} status updated: {old_status} -> {status}"
            )
            
            # Trigger tenant webhook if payment confirmed
            if status == 'paid':
                WebhookService.trigger_tenant_webhook(transaction)
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f"Error processing bank webhook: {e}")
            return False, f"Failed to process webhook: {str(e)}"
    
    @staticmethod
    def trigger_tenant_webhook(transaction: Transaction):
        """
        Trigger webhook notification to tenant.
        
        Args:
            transaction: Transaction instance
        """
        try:
            tenant = transaction.tenant
            
            if not tenant.webhook_url:
                current_app.logger.info(
                    f"No webhook URL configured for tenant {tenant.slug}"
                )
                return
            
            # Queue webhook task
            send_tenant_webhook.delay(str(transaction.id))
            
            current_app.logger.info(
                f"Webhook queued for tenant {tenant.slug}, transaction {transaction.txid}"
            )
            
        except Exception as e:
            current_app.logger.error(f"Error triggering tenant webhook: {e}")
    
    @staticmethod
    def validate_bank_webhook_signature(
        payload: Dict,
        signature: str,
        provider_name: str
    ) -> bool:
        """
        Validate webhook signature from bank.
        
        Args:
            payload: Webhook payload
            signature: Signature header
            provider_name: Bank provider name
            
        Returns:
            True if valid
        """
        # This is provider-specific
        # Each provider has its own signature validation method
        # For mock provider, we accept all
        
        if provider_name == 'mock':
            return True
        
        # Implement validation for specific providers
        # Example for Bradesco:
        # if provider_name == 'bradesco':
        #     return validate_bradesco_signature(payload, signature)
        
        current_app.logger.warning(
            f"Signature validation not implemented for provider: {provider_name}"
        )
        return False
