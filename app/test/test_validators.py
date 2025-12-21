import pytest
from app.utils.validators import validate_cpf


def test_valid_cpf_with_formatting():
    result = validate_cpf("123.456.789-09")
    assert result == "12345678909"


def test_valid_cpf_without_formatting():
    result = validate_cpf("12345678909")
    assert result == "12345678909"


def test_cpf_with_wrong_length():
    with pytest.raises(ValueError, match="CPF deve conter 11 dígitos"):
        validate_cpf("123456789")


def test_cpf_with_all_same_digits():
    with pytest.raises(ValueError, match="CPF inválido"):
        validate_cpf("111.111.111-11")


def test_cpf_with_invalid_check_digits():
    with pytest.raises(ValueError, match="CPF inválido"):
        validate_cpf("123.456.789-00")


def test_cpf_real_valid():
    valid_cpfs = [
        "11144477735",
        "52998224725",
    ]
    for cpf in valid_cpfs:
        result = validate_cpf(cpf)
        assert len(result) == 11

