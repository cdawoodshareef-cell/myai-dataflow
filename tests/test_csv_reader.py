"""Unit tests for csv_reader.py."""
import io
import pytest
from csv_reader import read_csv


def _make_file(text: str) -> io.BytesIO:
    """Helper: encode text as UTF-8 BytesIO (mimics Streamlit upload)."""
    return io.BytesIO(text.encode("utf-8"))


def test_valid_csv_returns_columns_and_rows():
    """Valid CSV with UTF-8 characters returns correct column names and data rows."""
    content = (
        "Invoice Number,Invoice Date,Supplier Name\n"
        "INV-001,2024-01-15,Acme Corp\n"
        "INV-002,2024-01-16,Béta Ltée\n"  # UTF-8 accented character
    )
    cols, rows = read_csv(_make_file(content))
    assert cols == ["Invoice Number", "Invoice Date", "Supplier Name"]
    assert len(rows) == 2
    assert rows[0] == ["INV-001", "2024-01-15", "Acme Corp"]
    assert rows[1] == ["INV-002", "2024-01-16", "Béta Ltée"]


def test_empty_file_raises_value_error():
    """Empty file raises ValueError."""
    with pytest.raises(ValueError, match="empty"):
        read_csv(_make_file(""))


def test_header_only_raises_value_error():
    """File with only a header row (no data) raises ValueError."""
    with pytest.raises(ValueError, match="no data rows"):
        read_csv(_make_file("Invoice Number,Invoice Date,Supplier Name\n"))


def test_values_preserved_without_modification():
    """Cell values are returned exactly as they appear — no stripping or alteration."""
    content = (
        "Col A,Col B\n"
        "  hello  , world \n"   # leading/trailing spaces preserved
        ",empty\n"              # empty cell preserved as empty string
    )
    cols, rows = read_csv(_make_file(content))
    assert rows[0] == ["  hello  ", " world "]
    assert rows[1] == ["", "empty"]


def test_over_wide_row_raises_value_error():
    """A data row with more fields than the header raises ValueError with row
    number, actual count, and expected count in the message."""
    # Header has 3 columns; row 2 (data row 2) has 5 fields
    content = (
        "Invoice Number,Invoice Date,Supplier Name\n"
        "INV-001,2024-01-15,Acme Corp\n"
        "INV-002,2024-01-16,Acme Corp,extra_field,another_extra\n"
    )
    with pytest.raises(ValueError) as exc_info:
        read_csv(_make_file(content))
    msg = str(exc_info.value)
    assert "row 2" in msg, f"Expected 'row 2' in error message, got: {msg}"
    assert "5" in msg, f"Expected actual field count '5' in message, got: {msg}"
    assert "3" in msg, f"Expected expected field count '3' in message, got: {msg}"
