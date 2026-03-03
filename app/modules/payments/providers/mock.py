"""
Mock payment provider for testing and development.
"""
import base64
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime, timedelta
import uuid
from app.modules.payments.providers.base import BankProvider, ProviderError


class MockProvider(BankProvider):
    """
    Mock provider that simulates payment processing.
    Useful for development and testing.
    """
    
    def create_charge(
        self,
        amount: Decimal,
        pix_key: str,
        description: Optional[str] = None,
        external_id: Optional[str] = None,
        expires_in_minutes: int = 60
    ) -> Dict:
        """Create a mock charge."""
        
        # Generate mock txid
        txid = f"MOCK{uuid.uuid4().hex[:16].upper()}"
        
        # Generate mock QR code (just a simple base64 string)
        qr_data = f"PIX|{pix_key}|{amount}|{txid}"
        qr_code_text = base64.b64encode(qr_data.encode()).decode()
        
        # Mock QR code image (in real scenario, this would be actual image data)
        qr_code = f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        return {
            'txid': txid,
            'qr_code': qr_code,
            'qr_code_text': qr_code_text,
            'expires_at': expires_at,
            'status': 'pending',
            'raw_response': {
                'provider': 'mock',
                'message': 'Mock charge created successfully',
                'amount': str(amount),
                'pix_key': pix_key,
                'external_id': external_id
            }
        }
    
    def get_charge_status(self, txid: str) -> Dict:
        """Get mock charge status."""
        
        # In mock, we just return pending
        # In a real scenario, you'd query the bank API
        return {
            'txid': txid,
            'status': 'pending',
            'amount': Decimal('0.00'),
            'paid_at': None,
            'payer': None,
            'raw_response': {
                'provider': 'mock',
                'message': 'Mock status check'
            }
        }
    
    def cancel_charge(self, txid: str) -> bool:
        """Cancel mock charge."""
        # Mock always succeeds
        return True
    
    def validate_webhook(self, payload: Dict, signature: str = None) -> bool:
        """Validate mock webhook."""
        # For mock, we accept all webhooks
        # In production, you'd verify signature
        return True


class BradescoProvider(BankProvider):
    """
    Example implementation for Bradesco bank.
    This is a placeholder - actual implementation would require Bradesco API credentials.
    """
    
    def create_charge(
        self,
        amount: Decimal,
        pix_key: str,
        description: Optional[str] = None,
        external_id: Optional[str] = None,
        expires_in_minutes: int = 60
    ) -> Dict:
        """
        Create charge with Bradesco API.
        
        NOTE: This is a placeholder implementation.
        Real implementation would use Bradesco's actual API endpoints.
        """
        raise ProviderError(
            "Bradesco provider not fully implemented. Please use mock provider or implement Bradesco API integration.",
            code="NOT_IMPLEMENTED"
        )
    
    def get_charge_status(self, txid: str) -> Dict:
        raise ProviderError("Bradesco provider not fully implemented", code="NOT_IMPLEMENTED")
    
    def cancel_charge(self, txid: str) -> bool:
        raise ProviderError("Bradesco provider not fully implemented", code="NOT_IMPLEMENTED")
    
    def validate_webhook(self, payload: Dict, signature: str = None) -> bool:
        raise ProviderError("Bradesco provider not fully implemented", code="NOT_IMPLEMENTED")
