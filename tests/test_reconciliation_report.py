from decimal import Decimal
import pytest
from reconciliation_report import generate_reconciliation_summary

COLS = ['Invoice Number', 'Supplier Name', 'Quantity', 'Unit Price', 'Total Amount']

def row(number, supplier, quantity, price, total):
    return [number, supplier, quantity, price, total]

def test_valid_invoice():
    result = generate_reconciliation_summary(COLS, [row('1', 'Apex', '5', '100', '500')])
    assert result['valid_invoices'] == 1
    assert result['total_discrepancy'] == Decimal('0.00')

def test_incorrect_invoice_total():
    result = generate_reconciliation_summary(COLS, [row('1', 'Apex', '5', '100', '450')])
    assert result['invalid_invoices'] == 1
    assert result['total_discrepancy'] == Decimal('50.00')

def test_duplicate_excluded_from_totals():
    invoice = row('1', 'Apex', '5', '100', '500')
    result = generate_reconciliation_summary(COLS, [invoice, invoice])
    assert result['duplicate_invoices'] == 1
    assert result['total_reported_amount'] == Decimal('500')
    assert result['valid_invoices'] == 1

def test_supplier_wise_summary():
    rows = [row('1', 'Apex', '2', '100', '200'), row('2', 'BlueStar', '3', '100', '250')]
    result = generate_reconciliation_summary(COLS, rows)
    assert result['supplier_summary']['Apex']['valid_invoices'] == 1
    assert result['supplier_summary']['BlueStar']['discrepancy'] == Decimal('50.00')

def test_invalid_quantity():
    result = generate_reconciliation_summary(COLS, [row('1', 'Apex', 'abc', '100', '200')])
    assert result['invalid_invoices'] == 1

def test_missing_quantity():
    result = generate_reconciliation_summary(COLS, [row('1', 'Apex', '', '100', '200')])
    assert result['invalid_invoices'] == 1

def test_decimal_rounding():
    result = generate_reconciliation_summary(COLS, [row('1', 'Apex', '3', '0.335', '1.01')])
    assert result['valid_invoices'] == 1

def test_missing_required_header():
    with pytest.raises(ValueError):
        generate_reconciliation_summary(['Supplier Name', 'Quantity'], [])

def test_invalid_invoice_does_not_disappear():
    result = generate_reconciliation_summary(COLS, [row('1', 'Apex', '5', '100', '450')])
    assert result['total_invoices'] == 1
    assert result['invalid_invoices'] == 1
    assert result['total_reported_amount'] == Decimal('450')


def test_missing_invoice_number():
    result = generate_reconciliation_summary(COLS, [row("", "Apex", "5", "100", "500")])
    assert result["invalid_invoices"] == 1
    assert result["valid_invoices"] == 0

def test_blank_supplier_is_invalid_and_uses_fallback_label():
    result = generate_reconciliation_summary(COLS, [row("1", "", "2", "100", "200")])
    assert result["invalid_invoices"] == 1
    assert result["valid_invoices"] == 0
    supplier = result["supplier_summary"]["Unknown supplier"]
    assert supplier["invalid_invoices"] == 1
    assert supplier["valid_invoices"] == 0

def test_whitespace_supplier_is_invalid_and_uses_fallback_label():
    result = generate_reconciliation_summary(COLS, [row("1", "   ", "2", "100", "200")])
    assert result["invalid_invoices"] == 1
    assert result["valid_invoices"] == 0
    supplier = result["supplier_summary"]["Unknown supplier"]
    assert supplier["invalid_invoices"] == 1
    assert supplier["valid_invoices"] == 0
