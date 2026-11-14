"""Unit tests for exporter.py."""
import csv
import io
import pytest
from validator import FlaggedRow
from exporter import generate_clean_csv, generate_review_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

COLS = [
    "Invoice Number", "Invoice Date", "Supplier Name", "Product Code",
    "Product Description", "Quantity", "Unit Price", "Total Amount",
]


def _parse_csv(data: bytes) -> list:
    """Decode bytes and parse as CSV, returning list of rows."""
    text = data.decode("utf-8")
    return list(csv.reader(io.StringIO(text)))


def _valid_row(n: int) -> list:
    return [f"INV-{n:03}", "2024-01-01", f"Supplier {n}", f"PC-{n:03}",
            f"Product {n}", "10", "9.99", "99.90"]


# ---------------------------------------------------------------------------
# generate_clean_csv tests
# ---------------------------------------------------------------------------

def test_clean_csv_has_correct_header_and_rows():
    """Clean CSV has the original header as row 0 and all clean rows follow."""
    rows = [_valid_row(1), _valid_row(2)]
    result = _parse_csv(generate_clean_csv(COLS, rows))
    assert result[0] == COLS
    assert result[1] == _valid_row(1)
    assert result[2] == _valid_row(2)
    assert len(result) == 3


def test_clean_csv_no_flagged_rows_present():
    """The clean CSV must not contain any rows that were not in the clean list."""
    clean = [_valid_row(1)]
    flagged_values = _valid_row(2)
    result = _parse_csv(generate_clean_csv(COLS, clean))
    assert flagged_values not in result


def test_clean_csv_empty_output_header_only():
    """When zero clean rows, output contains only the header row."""
    result = _parse_csv(generate_clean_csv(COLS, []))
    assert len(result) == 1
    assert result[0] == COLS


def test_clean_csv_is_utf8_encoded():
    """Output is valid UTF-8 bytes; non-ASCII values round-trip correctly."""
    rows = [["INV-001", "2024-01-01", "Béta Ltée", "PC-001", "Produit", "5", "1.00", "5.00"]]
    data = generate_clean_csv(COLS, rows)
    assert isinstance(data, bytes)
    decoded = data.decode("utf-8")
    assert "Béta Ltée" in decoded


# ---------------------------------------------------------------------------
# generate_review_report tests
# ---------------------------------------------------------------------------

def test_review_report_header_has_extra_columns_appended():
    """Review report header ends with 'Original Row Number' and 'Flag Reason'."""
    fr = FlaggedRow(row_number=1, row_values=_valid_row(1), reason="Test reason")
    result = _parse_csv(generate_review_report(COLS, [fr]))
    assert result[0] == COLS + [
        "Original Row Number",
        "Flag Reason",
        "Excel Row Number",
        "Duplicate of Excel Row",
    ]

def test_review_report_rows_in_ascending_row_number_order():
    """Rows are written in the order they are passed — caller sorts ascending."""
    frs = sorted([
        FlaggedRow(row_number=3, row_values=_valid_row(3), reason="reason 3"),
        FlaggedRow(row_number=1, row_values=_valid_row(1), reason="reason 1"),
        FlaggedRow(row_number=2, row_values=_valid_row(2), reason="reason 2"),
    ], key=lambda r: r.row_number)
    result = _parse_csv(generate_review_report(COLS, frs))
    row_number_index = result[0].index("Original Row Number")
    row_numbers = [int(row[row_number_index]) for row in result[1:]]
    assert row_numbers == [1, 2, 3]


def test_review_report_empty_header_only():
    """When no flagged rows, review report contains only the header."""
    result = _parse_csv(generate_review_report(COLS, []))
    assert len(result) == 1
    assert result[0] == COLS + [
        "Original Row Number",
        "Flag Reason",
        "Excel Row Number",
        "Duplicate of Excel Row",
    ]

def test_review_report_row_number_and_reason_correct():
    """Check the original row, flag reason, and Excel row fields."""
    fr = FlaggedRow(
        row_number=7,
        row_values=_valid_row(7),
        reason="Missing value in column(s): 'Quantity'",
    )
    result = _parse_csv(generate_review_report(COLS, [fr]))
    data_row = result[1]

    assert data_row[len(COLS):] == ["7", fr.reason, "8", ""]


def test_review_report_short_row_padded_correctly():
    """Pad short rows so all four review fields align with their headers."""
    short_values = ["INV-001", "2024-01-01", "Acme Corp"]
    fr = FlaggedRow(
        row_number=5,
        row_values=short_values,
        reason=(
            "Missing value in column(s): 'Product Code', 'Product Description', "
            "'Quantity', 'Unit Price', 'Total Amount'"
        ),
    )
    result = _parse_csv(generate_review_report(COLS, [fr]))
    data_row = result[1]

    assert len(data_row) == len(COLS) + 4
    assert data_row[:len(COLS)] == short_values + [""] * (len(COLS) - len(short_values))
    assert data_row[len(COLS):] == ["5", fr.reason, "6", ""]


# ---------------------------------------------------------------------------
# Reconciliation CSV exporter tests
# ---------------------------------------------------------------------------
from exporter import generate_reconciliation_csv

def _sample_reconciliation_summary():
    from decimal import Decimal
    return {
        "supplier_summary": {
            "Apex Wholesale": {"invoice_count": 2, "valid_invoices": 1, "invalid_invoices": 1, "reported_amount": Decimal("500.00"), "calculated_amount": Decimal("550.00"), "discrepancy": Decimal("50.00")},
            "BlueStar Supplies": {"invoice_count": 1, "valid_invoices": 1, "invalid_invoices": 0, "reported_amount": Decimal("300.00"), "calculated_amount": Decimal("300.00"), "discrepancy": Decimal("0.00")},
        },
        "duplicate_invoices": 2,
    }

def test_reconciliation_csv_header():
    result = _parse_csv(generate_reconciliation_csv(_sample_reconciliation_summary()))
    assert result[0] == ["Supplier Name", "Invoice Count", "Valid Invoices", "Invalid Invoices", "Reported Amount", "Calculated Amount", "Discrepancy"]

def test_reconciliation_csv_contains_supplier_names():
    result = _parse_csv(generate_reconciliation_csv(_sample_reconciliation_summary()))
    assert [row[0] for row in result[1:3]] == ["Apex Wholesale", "BlueStar Supplies"]

def test_reconciliation_csv_total_row():
    result = _parse_csv(generate_reconciliation_csv(_sample_reconciliation_summary()))
    total = result[-2]
    assert total[0] == "TOTAL (duplicates excluded)"
    assert total[1:] == ["3", "2", "1", "800.00", "850.00", "50.00"]

def test_reconciliation_csv_duplicate_exclusion_row():
    result = _parse_csv(generate_reconciliation_csv(_sample_reconciliation_summary()))
    assert result[-1] == ["Duplicate invoices excluded", "2", "", "", "", "", ""]

def test_reconciliation_csv_is_utf8_bytes():
    from decimal import Decimal
    summary = _sample_reconciliation_summary()
    summary["supplier_summary"]["Béta Supplies"] = {"invoice_count": 1, "valid_invoices": 1, "invalid_invoices": 0, "reported_amount": Decimal("10.00"), "calculated_amount": Decimal("10.00"), "discrepancy": Decimal("0.00")}
    data = generate_reconciliation_csv(summary)
    assert isinstance(data, bytes)
    assert "Béta Supplies" in data.decode("utf-8")

def test_reconciliation_csv_empty_supplier_summary():
    result = _parse_csv(generate_reconciliation_csv({"supplier_summary": {}, "duplicate_invoices": 0}))
    assert len(result) == 3
    assert result[1][0] == "TOTAL (duplicates excluded)"
    assert result[1][1:] == ["0", "0", "0", "0", "0", "0"]
