"""Property-based tests (Hypothesis) for csv-error-detective.

Each property is tagged with its design reference.
All properties use a minimum of 100 examples.
"""
from __future__ import annotations

import csv
import io
from typing import List

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

import csv_reader
import validator as val
from validator import REQUIRED_COLUMNS, FlaggedRow
import exporter

# ---------------------------------------------------------------------------
# Shared strategies and helpers
# ---------------------------------------------------------------------------

# Printable text that won't confuse CSV parsing (no newlines, no null bytes)
_safe_text = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs",),   # no surrogates
        blacklist_characters="\r\n\x00",
    ),
    min_size=0,
    max_size=30,
)

# A non-empty cell value (at least one non-whitespace character)
_non_empty_cell = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters="\r\n\x00",
    ),
    min_size=1,
    max_size=20,
).filter(lambda s: s.strip() != "")

# A fully valid row with positive quantity, price, and matching total
_valid_row_strategy = st.tuples(
    st.fixed_dictionaries({c: _non_empty_cell for c in REQUIRED_COLUMNS[:5]}),
    st.integers(min_value=1, max_value=10000),
    st.integers(min_value=1, max_value=100000),
).map(lambda values: [values[0][c] for c in REQUIRED_COLUMNS[:5]] + [str(values[1]), str(values[2] / 100) if False else format(__import__("decimal").Decimal(values[2]) / 100, ".2f"), format(__import__("decimal").Decimal(values[1]) * values[2] / 100, ".2f")])

COLS = list(REQUIRED_COLUMNS)


def _make_bytes(text: str) -> io.BytesIO:
    return io.BytesIO(text.encode("utf-8"))


def _csv_to_bytes(column_names: List[str], rows: List[List[str]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(column_names)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# P1: UTF-8 Round-Trip Preservation
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 1: UTF-8 Round-Trip Preservation
@settings(max_examples=100)
@given(
    rows=st.lists(
        st.lists(_safe_text, min_size=len(COLS), max_size=len(COLS)),
        min_size=1,
        max_size=10,
    )
)
def test_p1_utf8_round_trip(rows):
    """For any rows of safe strings, encoding as CSV and reading back produces
    identical values."""
    csv_bytes = _csv_to_bytes(COLS, rows)
    col_names, data_rows = csv_reader.read_csv(io.BytesIO(csv_bytes))
    assert col_names == COLS
    assert data_rows == rows


# ---------------------------------------------------------------------------
# P2: Whitespace-Only Cell Detection
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 2: Whitespace-Only Cell Detection
@settings(max_examples=100)
@given(
    whitespace=st.text(alphabet=" \t", min_size=1, max_size=10),
    col_idx=st.integers(min_value=0, max_value=len(REQUIRED_COLUMNS) - 1),
)
def test_p2_whitespace_only_cell_flagged_as_missing(whitespace, col_idx):
    """A cell containing only whitespace in a required column is treated as a
    Missing_Value."""
    row = ["val"] * len(COLS)
    row[col_idx] = whitespace
    result = val.validate_rows(COLS, [row])
    assert result.flagged_count == 1
    assert COLS[col_idx] in result.flagged_rows[0].reason


# ---------------------------------------------------------------------------
# P3: Missing Column Completeness
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 3: Missing Column Completeness
@settings(max_examples=100)
@given(
    missing_indices=st.frozensets(
        st.integers(min_value=0, max_value=len(REQUIRED_COLUMNS) - 1),
        min_size=1,
    )
)
def test_p3_missing_column_completeness(missing_indices):
    """When N required columns are missing from a row, all N column names appear
    in the reason string in header order."""
    row = ["val"] * len(COLS)
    for i in missing_indices:
        row[i] = ""
    result = val.validate_rows(COLS, [row])
    assert result.flagged_count == 1
    reason = result.flagged_rows[0].reason
    # All missing columns must be named, in header order
    expected_cols = [COLS[i] for i in sorted(missing_indices)]
    for col in expected_cols:
        assert col in reason, f"Expected '{col}' in reason: '{reason}'"
    # Columns must appear in header order within the reason
    positions = [reason.index(f"'{col}'") for col in expected_cols]
    assert positions == sorted(positions), f"Columns not in header order in: '{reason}'"


# ---------------------------------------------------------------------------
# P4: 1-Based Row Numbering
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 4: 1-Based Row Numbering
@settings(max_examples=100)
@given(row=st.lists(_safe_text, min_size=len(COLS), max_size=len(COLS)))
def test_p4_first_data_row_is_row_1(row):
    """When any row is the only data row and is flagged, its row_number is 1."""
    # Force a flag by blanking the first required column
    row[0] = ""
    result = val.validate_rows(COLS, [row])
    assert result.flagged_count >= 1
    assert result.flagged_rows[0].row_number == 1


# ---------------------------------------------------------------------------
# P5: Duplicate-Only Reason for Valid Duplicates
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 5: Duplicate-Only Reason for Valid Duplicates
@settings(max_examples=100)
@given(row=_valid_row_strategy)
def test_p5_duplicate_only_reason_for_valid_duplicates(row):
    """Two identical valid rows: first is clean, second is flagged with
    'Exact duplicate of row 1'."""
    result = val.validate_rows(COLS, [row, row])
    assert result.clean_count == 1
    assert result.flagged_count == 1
    assert result.clean_rows[0] == row
    assert result.flagged_rows[0].reason == "Exact duplicate of row 1"
    assert result.flagged_rows[0].row_number == 2


# ---------------------------------------------------------------------------
# P6: Missing-Only Reason Format
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 6: Missing-Only Reason Format
@settings(max_examples=100)
@given(
    row=_valid_row_strategy,
    col_idx=st.integers(min_value=0, max_value=len(REQUIRED_COLUMNS) - 1),
)
def test_p6_missing_only_reason_format(row, col_idx):
    """A row missing exactly one required value gets a reason in the exact format
    \"Missing value in column(s): 'ColName'\"."""
    row = list(row)
    row[col_idx] = ""
    result = val.validate_rows(COLS, [row])
    assert result.flagged_count == 1
    expected = f"Missing value in column(s): '{COLS[col_idx]}'"
    assert result.flagged_rows[0].reason == expected, (
        f"Expected: '{expected}'\nGot:      '{result.flagged_rows[0].reason}'"
    )


# ---------------------------------------------------------------------------
# P7: Combined Reason Format for Duplicate with Missing Values
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 7: Combined Reason Format for Duplicate with Missing Values
@settings(max_examples=100)
@given(
    base_row=_valid_row_strategy,
    col_idx=st.integers(min_value=0, max_value=len(REQUIRED_COLUMNS) - 1),
)
def test_p7_combined_reason_format(base_row, col_idx):
    """A row with a missing value that is also an exact duplicate of a prior row
    gets both reasons joined by '; ', duplicate reason first.
    Uses the scenario where p1 has a missing value (registered in seen),
    p2 is an exact copy (also missing) → flagged as dup + missing."""
    p1 = list(base_row)
    p1[col_idx] = ""          # first occurrence: missing value → flagged for missing, registered in seen
    p2 = list(p1)             # exact copy → true duplicate AND has missing value

    result = val.validate_rows(COLS, [p1, p2])

    assert result.flagged_count == 2
    # p1: missing only
    assert result.flagged_rows[0].reason.startswith("Missing value in column(s):")
    # p2: duplicate + missing
    fr = result.flagged_rows[1]
    assert fr.reason.startswith("Exact duplicate of row 1"), (
        f"Expected dup reason first, got: '{fr.reason}'"
    )
    assert "; Missing value in column(s):" in fr.reason, (
        f"Expected missing reason after '; ', got: '{fr.reason}'"
    )
    assert f"'{COLS[col_idx]}'" in fr.reason


# ---------------------------------------------------------------------------
# P8: Combined Reason References First Occurrence (not necessarily row 1)
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 8: Combined Reason References First Occurrence
@settings(max_examples=100)
@given(
    padding=st.lists(_valid_row_strategy, min_size=1, max_size=5),
    base_row=_valid_row_strategy,
    col_idx=st.integers(min_value=0, max_value=len(REQUIRED_COLUMNS) - 1),
)
def test_p8_combined_reason_references_first_occurrence(padding, base_row, col_idx):
    """When k valid padding rows precede a duplicate group, the duplicate reason
    in the combined reason references the FIRST occurrence row number (k+1),
    not row 1 or the current row.
    Uses the missing-first-occurrence scenario for combined reasons."""
    # Ensure padding rows are distinct from each other and from base_row
    assume(all(p != list(base_row) for p in padding))
    assume(len({tuple(p) for p in padding}) == len(padding))

    p1 = list(base_row)
    p1[col_idx] = ""    # first occurrence of this key, with missing value

    all_rows = padding + [p1, list(p1)]  # padding rows, then p1, then dup of p1
    first_occurrence_row_num = len(padding) + 1   # 1-based

    result = val.validate_rows(COLS, all_rows)

    # Find the flagged row that is a duplicate (has "Exact duplicate of row" in reason)
    dup_flags = [fr for fr in result.flagged_rows if "Exact duplicate of row" in fr.reason]
    assert len(dup_flags) >= 1, "Expected at least one duplicate-flagged row"

    for fr in dup_flags:
        expected_ref = f"Exact duplicate of row {first_occurrence_row_num}"
        assert fr.reason.startswith(expected_ref), (
            f"Expected reason to start with '{expected_ref}', got: '{fr.reason}'"
        )


# ---------------------------------------------------------------------------
# P9: Three Identical Rows — First Occurrence Rule
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 9: Three Identical Rows — First Occurrence Rule
@settings(max_examples=100)
@given(
    padding=st.lists(_valid_row_strategy, min_size=0, max_size=5),
    dup_row=_valid_row_strategy,
)
def test_p9_three_identical_rows_first_occurrence_rule(padding, dup_row):
    """Given k padding rows followed by 3 identical valid rows, clean output
    contains exactly one copy, and both later rows reference the first occurrence."""
    assume(all(p != list(dup_row) for p in padding))
    assume(len({tuple(p) for p in padding}) == len(padding))

    first_occurrence_num = len(padding) + 1
    all_rows = padding + [list(dup_row), list(dup_row), list(dup_row)]

    result = val.validate_rows(COLS, all_rows)

    # Exactly one copy in clean output
    clean_copies = [r for r in result.clean_rows if r == list(dup_row)]
    assert len(clean_copies) == 1, f"Expected 1 clean copy, got {len(clean_copies)}"

    # Exactly 2 flagged copies
    dup_flags = [fr for fr in result.flagged_rows if fr.row_values == list(dup_row)]
    assert len(dup_flags) == 2, f"Expected 2 duplicate flags, got {len(dup_flags)}"

    # Both reference the first occurrence
    for fr in dup_flags:
        expected = f"Exact duplicate of row {first_occurrence_num}"
        assert fr.reason == expected, (
            f"Expected '{expected}', got '{fr.reason}'"
        )


# ---------------------------------------------------------------------------
# P10: Short Row Missing Value Detection
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 10: Short Row Missing Value Detection
@settings(max_examples=100)
@given(
    n_fields=st.integers(min_value=0, max_value=len(REQUIRED_COLUMNS) - 1),
    values=st.lists(_non_empty_cell, min_size=0, max_size=len(REQUIRED_COLUMNS) - 1),
)
def test_p10_short_row_no_index_error(n_fields, values):
    """A row shorter than the header is flagged for the missing required columns
    it is short on. No IndexError is raised."""
    # Build a row with n_fields elements (fewer than 8)
    short_row = (values + ["x"] * len(REQUIRED_COLUMNS))[:n_fields]
    # Must have at least one absent required column
    assume(n_fields < len(REQUIRED_COLUMNS))

    result = val.validate_rows(COLS, [short_row])  # must not raise

    assert result.flagged_count >= 1
    reason = result.flagged_rows[0].reason
    # At minimum, columns from index n_fields onward must be named
    for col in REQUIRED_COLUMNS[n_fields:]:
        assert col in reason, f"Expected '{col}' in reason, got: '{reason}'"


# ---------------------------------------------------------------------------
# P11: Count Invariant
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 11: Count Invariant
@settings(max_examples=100)
@given(
    rows=st.lists(
        st.lists(_safe_text, min_size=len(COLS), max_size=len(COLS)),
        min_size=0,
        max_size=20,
    )
)
def test_p11_count_invariant(rows):
    """clean_count + flagged_count == total_count for any input."""
    result = val.validate_rows(COLS, rows)
    assert result.clean_count + result.flagged_count == result.total_count
    assert result.total_count == len(rows)


# ---------------------------------------------------------------------------
# P12: Sort Order of Flagged Rows in Review Report
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 12: Sort Order of Flagged Rows
@settings(max_examples=100)
@given(
    rows=st.lists(
        st.lists(_safe_text, min_size=len(COLS), max_size=len(COLS)),
        min_size=1,
        max_size=20,
    )
)
def test_p12_sort_order_of_flagged_rows(rows):
    """Flagged rows in the review report are listed in ascending row number order."""
    # Force at least one flag by blanking col 0 of every row
    flagged_rows = [[""] + r[1:] for r in rows]
    result = val.validate_rows(COLS, flagged_rows)
    assume(result.flagged_count > 0)

    report_bytes = exporter.generate_review_report(COLS, result.flagged_rows)
    parsed = list(csv.reader(io.StringIO(report_bytes.decode("utf-8"))))
    row_numbers = [int(r[-2]) for r in parsed[1:]]
    assert row_numbers == sorted(row_numbers), (
        f"Flagged rows not sorted: {row_numbers}"
    )


# ---------------------------------------------------------------------------
# P13: Clean Output Integrity
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 13: Clean Output Integrity
@settings(max_examples=100)
@given(
    rows=st.lists(
        st.lists(_safe_text, min_size=len(COLS), max_size=len(COLS)),
        min_size=1,
        max_size=20,
    )
)
def test_p13_clean_output_integrity(rows):
    """The clean CSV output contains no duplicate rows: every row key appears
    at most once in clean_rows.  Any subsequent occurrence of the same values
    must be in the flagged output, not the clean output."""
    result = val.validate_rows(COLS, rows)

    # Clean output must be internally duplicate-free
    seen_clean: set = set()
    for clean_row in result.clean_rows:
        key = tuple(clean_row)
        assert key not in seen_clean, (
            f"Duplicate row found in clean output: {clean_row}"
        )
        seen_clean.add(key)

    # Every flagged duplicate must reference a row key that IS in clean output
    # (the first occurrence) OR was itself flagged for missing values first.
    # We only verify the structural guarantee: clean output is duplicate-free.
    assert len(result.clean_rows) == len(seen_clean)


# ---------------------------------------------------------------------------
# P14: Review Report Schema Consistency (including short rows)
# ---------------------------------------------------------------------------
# Feature: csv-error-detective, Property 14: Review Report Schema Consistency
@settings(max_examples=100)
@given(
    n_values=st.integers(min_value=0, max_value=len(COLS) + 2),
    row_number=st.integers(min_value=1, max_value=1000),
    reason=_safe_text,
)
def test_p14_review_report_schema_consistency(n_values, row_number, reason):
    """Keep review fields aligned for short and over-wide input rows."""
    row_values = ["x"] * n_values
    fr = FlaggedRow(row_number=row_number, row_values=row_values, reason=reason)

    report_bytes = exporter.generate_review_report(COLS, [fr])
    parsed = list(csv.reader(io.StringIO(report_bytes.decode("utf-8"))))

    assert parsed[0] == COLS + [
        "Original Row Number",
        "Flag Reason",
        "Excel Row Number",
        "Duplicate of Excel Row",
    ]
    assert len(parsed[1]) == len(COLS) + 4
    assert parsed[1][len(COLS):] == [
        str(row_number),
        reason,
        str(row_number + 1),
        "",
    ]