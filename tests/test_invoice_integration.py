from validator import validate_rows, REQUIRED_COLUMNS


def test_incorrect_invoice_total_is_flagged():
    row = ["INV-001", "2024-01-01", "Sample Supplier", "P-001", "Sample Product", "5", "250.00", "1200.00"]
    result = validate_rows(REQUIRED_COLUMNS, [row])
    assert result.flagged_count == 1
    assert "invoice" in result.flagged_rows[0].reason.lower() or "amount" in result.flagged_rows[0].reason.lower()
