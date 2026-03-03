"""
Factory for creating payment provider instances.
"""
from typing import Dict, Optional
from flask import current_app
from app.modules.payments.providers.base import BankProvider, ProviderError
from app.modules.payments.providers.mock import MockProvider, BradescoProvider


def get_provider(provider_name: str, credentials: Optional[Dict] = None, config: Optional[Dict] = None) -> BankProvider:
    """
    Factory function to get a payment provider instance.
    
    Args:
        provider_name: Name of the provider ('mock', 'bradesco', etc.)
        credentials: Provider credentials
        config: Additional configuration
        
    Returns:
        BankProvider instance
        
    Raises:
        ProviderError: If provider is not found
    """
    providers = {
        'mock': MockProvider,
        'bradesco': BradescoProvider,
        # Add more providers here as they are implemented
        # 'inter': InterProvider,
        # 'openPix': OpenPixProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    
    if not provider_class:
        raise ProviderError(
            f"Unknown payment provider: {provider_name}",
            code="UNKNOWN_PROVIDER"
        )
    
    # Use default config from app if not provided
    if config is None:
        config = {
            'api_url': current_app.config.get('BANK_API_URL'),
            'timeout': current_app.config.get('BANK_TIMEOUT', 30)
        }
    
    return provider_class(credentials or {}, config)
