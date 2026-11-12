"""Unit tests for validator.py."""
import pytest
from validator import validate_rows, REQUIRED_COLUMNS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

COLS = [
    "Invoice Number", "Invoice Date", "Supplier Name", "Product Code",
    "Product Description", "Quantity", "Unit Price", "Total Amount",
]

def _valid_row(n: int) -> list:
    """Return a fully valid row with unique values keyed on n."""
    return [f"INV-{n:03}", "2024-01-01", f"Supplier {n}", f"PC-{n:03}",
            f"Product {n}", "10", "9.99", "99.90"]


# ---------------------------------------------------------------------------
# Task 5.3 — Core validation cases
# ---------------------------------------------------------------------------

def test_missing_required_column_in_header_raises():
    cols = [c for c in COLS if c != "Quantity"]
    with pytest.raises(ValueError, match="Quantity"):
        validate_rows(cols, [_valid_row(1)])


def test_single_missing_value_flagged_with_correct_reason():
    row = _valid_row(1)
    row[COLS.index("Invoice Number")] = ""
    result = validate_rows(COLS, [row])
    assert result.flagged_count == 1
    assert result.flagged_rows[0].reason == "Missing value in column(s): 'Invoice Number'"


def test_multiple_missing_values_all_named_in_header_order():
    row = _valid_row(1)
    row[COLS.index("Quantity")] = "   "
    row[COLS.index("Unit Price")] = ""
    result = validate_rows(COLS, [row])
    assert result.flagged_count == 1
    assert result.flagged_rows[0].reason == "Missing value in column(s): 'Quantity', 'Unit Price'"


def test_first_valid_duplicate_in_clean_second_flagged():
    row = _valid_row(1)
    result = validate_rows(COLS, [row, row])
    assert result.clean_count == 1
    assert result.flagged_count == 1
    assert result.flagged_rows[0].reason == "Exact duplicate of row 1"
    assert result.flagged_rows[0].row_number == 2


def test_first_occurrence_with_missing_values_flagged_for_missing_only():
    row = _valid_row(1)
    row[COLS.index("Quantity")] = ""
    result = validate_rows(COLS, [row, row])
    assert result.flagged_count == 2
    assert result.flagged_rows[0].reason == "Missing value in column(s): 'Quantity'"
    assert "Exact duplicate" in result.flagged_rows[1].reason


def test_clean_row_in_clean_output_only():
    result = validate_rows(COLS, [_valid_row(1)])
    assert result.clean_count == 1
    assert result.flagged_count == 0
    assert result.clean_rows[0] == _valid_row(1)


def test_all_valid_rows_no_flags():
    rows = [_valid_row(i) for i in range(1, 6)]
    result = validate_rows(COLS, rows)
    assert result.flagged_count == 0
    assert result.clean_count == 5
    assert result.total_count == 5


def test_all_flagged_clean_output_empty():
    row = _valid_row(1)
    row[COLS.index("Invoice Number")] = ""
    result = validate_rows(COLS, [row])
    assert result.clean_count == 0
    assert result.flagged_count == 1
    assert result.total_count == 1


# ---------------------------------------------------------------------------
# Task 5.4 — Three identical rows at positions 4, 5, 6
# ---------------------------------------------------------------------------

def test_three_identical_rows_at_positions_4_5_6():
    """
    Rows 1-3 are distinct and valid. Rows 4, 5, 6 are identical and valid.
    Row 4 must be in clean output.
    Rows 5 and 6 must both say 'Exact duplicate of row 4' (not row 5).
    """
    rows = [_valid_row(i) for i in range(1, 4)]   # rows 1, 2, 3
    dup_row = _valid_row(99)                        # rows 4, 5, 6 — identical
    rows += [dup_row, dup_row, dup_row]

    result = validate_rows(COLS, rows)

    # Row 4 must be clean
    assert any(r == dup_row for r in result.clean_rows), \
        "Row 4 (first occurrence) should be in clean output"

    # Exactly 2 flagged rows that are duplicates of dup_row
    dup_flags = [fr for fr in result.flagged_rows if fr.row_values == dup_row]
    assert len(dup_flags) == 2, f"Expected 2 duplicate flags, got {len(dup_flags)}"

    # Both must reference row 4
    for fr in dup_flags:
        assert fr.reason == "Exact duplicate of row 4", \
            f"Expected 'Exact duplicate of row 4', got '{fr.reason}'"

    # Row numbers must be 5 and 6
    assert sorted(fr.row_number for fr in dup_flags) == [5, 6]


# ---------------------------------------------------------------------------
# Task 5.5 — Duplicate with missing required value (separate from 5.4)
# ---------------------------------------------------------------------------

def test_duplicate_with_missing_value_gets_both_reasons():
    """
    p1 at position 1 has Quantity blank — flagged for missing only, registered in seen.
    p2 at position 2 is an exact copy of p1 (also Quantity blank) — flagged as both
    exact duplicate of row 1 AND missing Quantity, with duplicate reason first.
    """
    p1 = list(_valid_row(1))
    p1[COLS.index("Quantity")] = ""  # first occurrence: missing Quantity

    p2 = list(p1)  # exact copy → true duplicate AND has missing value

    result = validate_rows(COLS, [p1, p2])

    assert result.clean_count == 0
    assert result.flagged_count == 2

    # p1 flagged for missing only
    assert result.flagged_rows[0].row_number == 1
    assert result.flagged_rows[0].reason == "Missing value in column(s): 'Quantity'"

    # p2 flagged for both: duplicate first, then missing
    fr = result.flagged_rows[1]
    assert fr.row_number == 2
    assert fr.reason == "Exact duplicate of row 1; Missing value in column(s): 'Quantity'", \
        f"Got: '{fr.reason}'"


# ---------------------------------------------------------------------------
# Task 5.6 — Short row (fewer fields than header)
# ---------------------------------------------------------------------------

def test_short_row_flagged_no_index_error():
    """
    A row with fewer fields than the header is flagged for the absent required
    columns. No IndexError is raised.
    """
    short_row = ["INV-001", "2024-01-01", "Acme Corp"]  # only 3 of 8 fields
    result = validate_rows(COLS, [short_row])

    assert result.flagged_count == 1
    reason = result.flagged_rows[0].reason
    for col in ["Product Code", "Product Description", "Quantity", "Unit Price", "Total Amount"]:
        assert col in reason, f"Expected '{col}' in reason, got: '{reason}'"
