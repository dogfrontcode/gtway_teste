"""
Security utilities for encryption and signatures.
"""
import hmac
import hashlib
import base64
import json
from typing import Any, Dict
from cryptography.fernet import Fernet
from flask import current_app


def get_fernet() -> Fernet:
    """Get Fernet cipher instance with app's encryption key."""
    key = current_app.config['ENCRYPTION_KEY'].encode()
    # Ensure key is proper length for Fernet (32 bytes base64-encoded = 44 chars)
    if len(key) < 32:
        key = key.ljust(32, b'0')
    key = base64.urlsafe_b64encode(key[:32])
    return Fernet(key)


def encrypt_data(data: Dict[str, Any]) -> str:
    """
    Encrypt sensitive data (like bank credentials).
    
    Args:
        data: Dictionary to encrypt
        
    Returns:
        Encrypted string
    """
    try:
        fernet = get_fernet()
        json_data = json.dumps(data)
        encrypted = fernet.encrypt(json_data.encode())
        return encrypted.decode()
    except Exception as e:
        current_app.logger.error(f"Encryption error: {e}")
        raise


def decrypt_data(encrypted_string: str) -> Dict[str, Any]:
    """
    Decrypt encrypted data.
    
    Args:
        encrypted_string: Encrypted string
        
    Returns:
        Decrypted dictionary
    """
    try:
        fernet = get_fernet()
        decrypted = fernet.decrypt(encrypted_string.encode())
        return json.loads(decrypted.decode())
    except Exception as e:
        current_app.logger.error(f"Decryption error: {e}")
        raise


def generate_signature(payload: Dict[str, Any], secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for webhook payloads.
    
    Args:
        payload: Data to sign
        secret: Secret key
        
    Returns:
        Hex-encoded signature
    """
    message = json.dumps(payload, sort_keys=True).encode()
    signature = hmac.new(
        secret.encode(),
        message,
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_signature(payload: Dict[str, Any], signature: str, secret: str) -> bool:
    """
    Verify HMAC-SHA256 signature.
    
    Args:
        payload: Data to verify
        signature: Signature to check
        secret: Secret key
        
    Returns:
        True if signature is valid
    """
    expected_signature = generate_signature(payload, secret)
    return hmac.compare_digest(signature, expected_signature)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage.
    
    Args:
        api_key: API key to hash
        
    Returns:
        Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()
