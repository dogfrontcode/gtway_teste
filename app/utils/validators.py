"""
Validation utilities for common data formats.
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_cnpj(cnpj: str) -> bool:
    """
    Validate Brazilian CNPJ (company registration number).
    
    Args:
        cnpj: CNPJ string (with or without formatting)
        
    Returns:
        True if valid
    """
    # Remove non-digit characters
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Check length
    if len(cnpj) != 14:
        return False
    
    # Check if all digits are the same (invalid CNPJ)
    if cnpj == cnpj[0] * 14:
        return False
    
    # Validate first check digit
    weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights[i] for i in range(12))
    remainder = sum_digits % 11
    first_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cnpj[12]) != first_digit:
        return False
    
    # Validate second check digit
    weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights[i] for i in range(13))
    remainder = sum_digits % 11
    second_digit = 0 if remainder < 2 else 11 - remainder
    
    return int(cnpj[13]) == second_digit


def validate_cpf(cpf: str) -> bool:
    """
    Validate Brazilian CPF (individual registration number).
    
    Args:
        cpf: CPF string (with or without formatting)
        
    Returns:
        True if valid
    """
    # Remove non-digit characters
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Check length
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same (invalid CPF)
    if cpf == cpf[0] * 11:
        return False
    
    # Validate first check digit
    sum_digits = sum(int(cpf[i]) * (10 - i) for i in range(9))
    remainder = sum_digits % 11
    first_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cpf[9]) != first_digit:
        return False
    
    # Validate second check digit
    sum_digits = sum(int(cpf[i]) * (11 - i) for i in range(10))
    remainder = sum_digits % 11
    second_digit = 0 if remainder < 2 else 11 - remainder
    
    return int(cpf[10]) == second_digit


def validate_pix_key(pix_key: str, key_type: Optional[str] = None) -> bool:
    """
    Validate PIX key format.
    
    Args:
        pix_key: PIX key string
        key_type: Type of key ('email', 'cpf', 'cnpj', 'phone', 'random')
        
    Returns:
        True if valid
    """
    if not pix_key:
        return False
    
    # If type is specified, validate accordingly
    if key_type == 'email':
        return validate_email(pix_key)
    elif key_type == 'cpf':
        return validate_cpf(pix_key)
    elif key_type == 'cnpj':
        return validate_cnpj(pix_key)
    elif key_type == 'phone':
        # Brazilian phone: +55 followed by 10 or 11 digits
        phone = re.sub(r'[^0-9]', '', pix_key)
        return len(phone) >= 10 and len(phone) <= 13
    elif key_type == 'random':
        # Random key: UUID format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, pix_key.lower()))
    
    # If no type specified, try to detect and validate
    # Email
    if '@' in pix_key:
        return validate_email(pix_key)
    
    # Phone
    if '+' in pix_key or len(re.sub(r'[^0-9]', '', pix_key)) >= 10:
        phone = re.sub(r'[^0-9]', '', pix_key)
        return len(phone) >= 10 and len(phone) <= 13
    
    # CPF/CNPJ
    digits_only = re.sub(r'[^0-9]', '', pix_key)
    if len(digits_only) == 11:
        return validate_cpf(digits_only)
    elif len(digits_only) == 14:
        return validate_cnpj(digits_only)
    
    # Random key
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if re.match(uuid_pattern, pix_key.lower()):
        return True
    
    return False


def sanitize_slug(text: str) -> str:
    """
    Convert text to a URL-safe slug.
    
    Args:
        text: Text to convert
        
    Returns:
        URL-safe slug
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove accents and special characters
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text
