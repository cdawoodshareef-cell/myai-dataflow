from currency_validator import is_supported_currency

def test_inr_is_supported():
    assert is_supported_currency("INR") is True

def test_unsupported_currency():
    assert is_supported_currency("XYZ") is False

def test_lowercase_currency():
    assert is_supported_currency("usd") is True

def test_currency_with_spaces():
    assert is_supported_currency(" INR ") is True

def test_empty_currency():
    assert is_supported_currency("") is False

def test_none_currency():
    assert is_supported_currency(None) is False

def test_numeric_currency():
    assert is_supported_currency(123) is False
