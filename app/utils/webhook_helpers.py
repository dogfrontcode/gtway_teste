"""
Webhook utilities for sending notifications and handling retries.
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import current_app


class WebhookError(Exception):
    """Custom exception for webhook errors."""
    pass


def calculate_next_retry(attempt_number: int, base: int = 2) -> datetime:
    """
    Calculate next retry time using exponential backoff.
    
    Args:
        attempt_number: Current attempt number (1-indexed)
        base: Base for exponential calculation
        
    Returns:
        Next retry datetime
    """
    # Exponential backoff: base^(attempt-1) minutes
    # Attempt 1: immediate (0 min)
    # Attempt 2: 2 minutes
    # Attempt 3: 4 minutes
    # Attempt 4: 8 minutes
    # Attempt 5: 16 minutes
    delay_minutes = base ** (attempt_number - 1)
    return datetime.utcnow() + timedelta(minutes=delay_minutes)


def send_webhook(
    url: str,
    payload: Dict[str, Any],
    secret: Optional[str] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Send webhook notification to a URL.
    
    Args:
        url: Destination URL
        payload: Data to send
        secret: Optional secret for signature
        timeout: Request timeout in seconds
        
    Returns:
        Dict with status, response, and error information
        
    Raises:
        WebhookError: If webhook delivery fails
    """
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'PaymentGateway-Webhook/1.0'
    }
    
    # Add signature if secret provided
    if secret:
        from app.utils.security import generate_signature
        signature = generate_signature(payload, secret)
        headers['X-Webhook-Signature'] = signature
    
    result = {
        'success': False,
        'status_code': None,
        'response_body': None,
        'error': None
    }
    
    try:
        current_app.logger.info(f"Sending webhook to {url}")
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=timeout,
            allow_redirects=False
        )
        
        result['status_code'] = response.status_code
        result['response_body'] = response.text[:1000]  # Limit response size
        
        # Consider 2xx status codes as success
        if 200 <= response.status_code < 300:
            result['success'] = True
            current_app.logger.info(f"Webhook delivered successfully: {response.status_code}")
        else:
            result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
            current_app.logger.warning(f"Webhook failed with status {response.status_code}")
        
    except requests.exceptions.Timeout:
        result['error'] = f"Request timeout after {timeout} seconds"
        current_app.logger.error(f"Webhook timeout: {url}")
        
    except requests.exceptions.ConnectionError as e:
        result['error'] = f"Connection error: {str(e)[:200]}"
        current_app.logger.error(f"Webhook connection error: {e}")
        
    except requests.exceptions.RequestException as e:
        result['error'] = f"Request error: {str(e)[:200]}"
        current_app.logger.error(f"Webhook request error: {e}")
        
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)[:200]}"
        current_app.logger.error(f"Webhook unexpected error: {e}")
    
    return result


def validate_webhook_signature(payload: Dict[str, Any], signature: str, secret: str) -> bool:
    """
    Validate incoming webhook signature.
    
    Args:
        payload: Webhook payload
        signature: Provided signature
        secret: Secret key
        
    Returns:
        True if signature is valid
    """
    from app.utils.security import verify_signature
    
    try:
        return verify_signature(payload, signature, secret)
    except Exception as e:
        current_app.logger.error(f"Signature validation error: {e}")
        return False
