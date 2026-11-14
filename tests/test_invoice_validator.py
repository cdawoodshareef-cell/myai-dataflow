from decimal import Decimal
from invoice_validator import calculate_invoice_total

def test_calculate_invoice_total():
    assert calculate_invoice_total("125", "149.75") == Decimal("18718.75")


def test_valid_invoice_amount():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount("5", "250.00", "1250.00") is True


def test_invalid_invoice_amount():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount("5", "250.00", "1200.00") is False


def test_blank_quantity():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount("", "250.00", "1250.00") is False


def test_nonnumeric_quantity():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount("abc", "250.00", "1250.00") is False


def test_nan_quantity():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount("NaN", "250.00", "1250.00") is False


def test_blank_unit_price():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount('5', '', '1250.00') is False


def test_invalid_unit_price():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount('5', 'abc', '1250.00') is False


def test_blank_reported_total():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount('5', '250.00', '') is False


def test_invalid_reported_total():
    from invoice_validator import validate_invoice_amount
    assert validate_invoice_amount('5', '250.00', 'abc') is False
