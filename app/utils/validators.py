import re
from decimal import Decimal


def validate_cpf(cpf: str) -> str:
    cpf_clean = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf_clean) != 11:
        raise ValueError('CPF deve conter 11 dígitos')
    
    if cpf_clean == cpf_clean[0] * 11:
        raise ValueError('CPF inválido')
    
    sum_digits = sum(int(cpf_clean[i]) * (10 - i) for i in range(9))
    remainder = sum_digits % 11
    first_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cpf_clean[9]) != first_digit:
        raise ValueError('CPF inválido')
    
    sum_digits = sum(int(cpf_clean[i]) * (11 - i) for i in range(10))
    remainder = sum_digits % 11
    second_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cpf_clean[10]) != second_digit:
        raise ValueError('CPF inválido')
    
    return cpf_clean


def validate_volume_positive(volume: Decimal) -> Decimal:
    """Validate that the provided volume is greater than zero.

    This is a business-related validation but placed in the shared
    validators module so it's used consistently by schemas.
    """
    if volume <= 0:
        raise ValueError('Volume deve ser maior que zero')
    return volume

