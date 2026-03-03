"""
Abstract base class for payment providers.
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime


class BankProvider(ABC):
    """
    Abstract interface for bank/PSP integrations.
    Each provider must implement these methods.
    """
    
    def __init__(self, credentials: Dict, config: Dict = None):
        """
        Initialize provider with credentials.
        
        Args:
            credentials: Bank API credentials
            config: Additional configuration
        """
        self.credentials = credentials
        self.config = config or {}
    
    @abstractmethod
    def create_charge(
        self,
        amount: Decimal,
        pix_key: str,
        description: Optional[str] = None,
        external_id: Optional[str] = None,
        expires_in_minutes: int = 60
    ) -> Dict:
        """
        Create a new payment charge.
        
        Args:
            amount: Amount in currency
            pix_key: PIX key to receive payment
            description: Payment description
            external_id: External reference ID
            expires_in_minutes: Expiration time in minutes
            
        Returns:
            Dict with charge data:
            {
                'txid': 'transaction_id',
                'qr_code': 'base64_image_or_url',
                'qr_code_text': 'pix_copy_paste_code',
                'expires_at': datetime,
                'status': 'pending',
                'raw_response': {...}  # Full bank response
            }
            
        Raises:
            ProviderError: If charge creation fails
        """
        pass
    
    @abstractmethod
    def get_charge_status(self, txid: str) -> Dict:
        """
        Get the status of a charge.
        
        Args:
            txid: Transaction ID
            
        Returns:
            Dict with status data:
            {
                'txid': 'transaction_id',
                'status': 'pending|paid|expired|cancelled',
                'amount': Decimal,
                'paid_at': datetime or None,
                'payer': {...} or None,
                'raw_response': {...}
            }
            
        Raises:
            ProviderError: If status check fails
        """
        pass
    
    @abstractmethod
    def cancel_charge(self, txid: str) -> bool:
        """
        Cancel a pending charge.
        
        Args:
            txid: Transaction ID
            
        Returns:
            True if cancelled successfully
            
        Raises:
            ProviderError: If cancellation fails
        """
        pass
    
    @abstractmethod
    def validate_webhook(self, payload: Dict, signature: str = None) -> bool:
        """
        Validate incoming webhook from bank.
        
        Args:
            payload: Webhook payload
            signature: Signature header (if applicable)
            
        Returns:
            True if webhook is valid
        """
        pass


class ProviderError(Exception):
    """Exception raised by payment providers."""
    
    def __init__(self, message: str, code: str = None, details: Dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
