"""
CNPJ validator utility.
"""
import re


def validate_cnpj(cnpj: str) -> bool:
    """
    Validate Brazilian CNPJ number.
    
    Args:
        cnpj: CNPJ string (can have formatting)
        
    Returns:
        True if valid, False otherwise
    """
    if not cnpj:
        return False
    
    # Remove formatting
    cnpj = re.sub(r'[^\d]', '', cnpj)
    
    # CNPJ must have 14 digits
    if len(cnpj) != 14:
        return False
    
    # Reject known invalid CNPJs (all same digit)
    if cnpj in [s * 14 for s in '0123456789']:
        return False
    
    # Validate first check digit
    sum_digits = sum(int(cnpj[i]) * weight for i, weight in enumerate([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]))
    digit1 = 11 - (sum_digits % 11)
    digit1 = 0 if digit1 >= 10 else digit1
    
    if int(cnpj[12]) != digit1:
        return False
    
    # Validate second check digit
    sum_digits = sum(int(cnpj[i]) * weight for i, weight in enumerate([6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]))
    digit2 = 11 - (sum_digits % 11)
    digit2 = 0 if digit2 >= 10 else digit2
    
    if int(cnpj[13]) != digit2:
        return False
    
    return True


def format_cnpj(cnpj: str) -> str:
    """
    Format CNPJ with mask: XX.XXX.XXX/XXXX-XX
    
    Args:
        cnpj: CNPJ string (numbers only)
        
    Returns:
        Formatted CNPJ
    """
    cnpj = re.sub(r'[^\d]', '', cnpj)
    
    if len(cnpj) != 14:
        return cnpj
    
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def validate_cpf(cpf: str) -> bool:
    """
    Validate Brazilian CPF number.
    
    Args:
        cpf: CPF string (can have formatting)
        
    Returns:
        True if valid, False otherwise
    """
    if not cpf:
        return False
    
    # Remove formatting
    cpf = re.sub(r'[^\d]', '', cpf)
    
    # CPF must have 11 digits
    if len(cpf) != 11:
        return False
    
    # Reject known invalid CPFs (all same digit)
    if cpf in [s * 11 for s in '0123456789']:
        return False
    
    # Validate first check digit
    sum_digits = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit1 = 11 - (sum_digits % 11)
    digit1 = 0 if digit1 >= 10 else digit1
    
    if int(cpf[9]) != digit1:
        return False
    
    # Validate second check digit
    sum_digits = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit2 = 11 - (sum_digits % 11)
    digit2 = 0 if digit2 >= 10 else digit2
    
    if int(cpf[10]) != digit2:
        return False
    
    return True


def format_cpf(cpf: str) -> str:
    """
    Format CPF with mask: XXX.XXX.XXX-XX
    
    Args:
        cpf: CPF string (numbers only)
        
    Returns:
        Formatted CPF
    """
    cpf = re.sub(r'[^\d]', '', cpf)
    
    if len(cpf) != 11:
        return cpf
    
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def validate_document(document: str) -> bool:
    """
    Validate CPF or CNPJ automatically.
    
    Args:
        document: CPF or CNPJ string
        
    Returns:
        True if valid, False otherwise
    """
    document = re.sub(r'[^\d]', '', document)
    
    if len(document) == 11:
        return validate_cpf(document)
    elif len(document) == 14:
        return validate_cnpj(document)
    
    return False
