from validator import validate_rows, REQUIRED_COLUMNS


def test_incorrect_invoice_total_is_flagged():
    row = ["INV-001", "2024-01-01", "Sample Supplier", "P-001", "Sample Product", "5", "250.00", "1200.00"]
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1
    assert "invoice" in result.flagged_rows[0].reason.lower() or "amount" in result.flagged_rows[0].reason.lower()


def test_zero_quantity_is_flagged():
    row = ["INV-002", "2024-01-01", "Sample Supplier", "P-002", "Sample Product", "0", "250.00", "0.00"]
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1
    assert "Invalid invoice amount" in result.flagged_rows[0].reason


def test_negative_quantity_is_flagged():
    row = ["INV-003", "2024-01-01", "Sample Supplier", "P-003", "Sample Product", "-5", "250.00", "-1250.00"]
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1
    assert "Invalid invoice amount" in result.flagged_rows[0].reason


def test_negative_price_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '5', '-250.00', '-1250.00']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1


def test_zero_price_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '5', '0', '0.00']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1


def test_text_quantity_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', 'abc', '250.00', '1250.00']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1


def test_text_price_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '5', 'abc', '1250.00']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1


def test_text_total_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '5', '250.00', 'abc']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1


def test_incorrect_total_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '5', '250.00', '1000.00']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1


def test_valid_total_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '5', '250.00', '1250.00']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 0


def test_decimal_quantity_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '2.5', '100.00', '250.00']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 0


def test_missing_quantity_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '', '250.00', '1250.00']
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1


def test_duplicate_valid_invoice_integration():
    row = ['INV-100', '2024-01-01', 'Sample Supplier', 'P-100', 'Sample Product', '5', '250.00', '1250.00']
    result = validate_rows(REQUIRED_COLUMNS, [row, row])
    assert result.clean_count == 1
    assert result.flagged_count == 1
    assert "duplicate" in result.flagged_rows[0].reason.lower()
