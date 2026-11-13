"""validator.py — Row validation and duplicate detection."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

REQUIRED_COLUMNS: List[str] = [
    "Invoice Number",
    "Invoice Date",
    "Supplier Name",
    "Product Code",
    "Product Description",
    "Quantity",
    "Unit Price",
    "Total Amount",
]


@dataclass
class FlaggedRow:
    row_number: int
    row_values: List[str]
    reason: str
    duplicate_of_row: int | None = None


@dataclass
class ValidationResult:
    clean_rows: List[List[str]] = field(default_factory=list)
    flagged_rows: List[FlaggedRow] = field(default_factory=list)
    total_count: int = 0
    clean_count: int = 0
    flagged_count: int = 0


def validate_rows(
    column_names: List[str],
    data_rows: List[List[str]],
) -> ValidationResult:
    """Validate rows for missing values and exact duplicates.

    Args:
        column_names: List of column names from the header row.
        data_rows: List of data rows; each row is a list of strings.

    Returns:
        ValidationResult containing clean rows, flagged rows, and counts.

    Raises:
        ValueError: If any Required_Column is absent from column_names.
    """
    # Normalise header for case-insensitive matching
    normalised = {c.strip().lower(): i for i, c in enumerate(column_names)}

    # Verify all required columns are present
    missing_required = [
        rc for rc in REQUIRED_COLUMNS
        if rc.strip().lower() not in normalised
    ]
    if missing_required:
        names = ", ".join(f"'{c}'" for c in missing_required)
        raise ValueError(f"Missing required columns: {names}")

    # Build ordered list of (required_col_name, index_in_row)
    required_indices: List[Tuple[str, int]] = [
        (rc, normalised[rc.strip().lower()]) for rc in REQUIRED_COLUMNS
    ]

    seen: Dict[Tuple[str, ...], int] = {}
    clean_rows: List[List[str]] = []
    flagged_rows: List[FlaggedRow] = []

    for row_number, row in enumerate(data_rows, start=1):
        row_key = tuple(row)

        # --- Missing value check ---
        missing_cols = [
            col_name
            for col_name, idx in required_indices
            if (row[idx] if idx < len(row) else "").strip() == ""
        ]
        missing_reason = (
            "Missing value in column(s): "
            + ", ".join(f"'{c}'" for c in missing_cols)
        ) if missing_cols else ""

        # --- Duplicate check ---
        duplicate_of_row = seen.get(row_key)
        is_dup = duplicate_of_row is not None
        dup_reason = f"Exact duplicate of row {duplicate_of_row}" if is_dup else ""

        # --- Register first occurrence (always, regardless of validity) ---
        if not is_dup:
            seen[row_key] = row_number

        # --- Flagging decision ---
        if is_dup and missing_cols:
            reason = f"{dup_reason}; {missing_reason}"
            flagged_rows.append(
                FlaggedRow(row_number, list(row), reason, duplicate_of_row=duplicate_of_row)
            )
        elif is_dup:
            flagged_rows.append(
                FlaggedRow(row_number, list(row), dup_reason, duplicate_of_row=duplicate_of_row)
            )
        elif missing_cols:
            flagged_rows.append(FlaggedRow(row_number, list(row), missing_reason))
        else:
            clean_rows.append(list(row))

    total = len(data_rows)
    flagged = len(flagged_rows)
    return ValidationResult(
        clean_rows=clean_rows,
        flagged_rows=flagged_rows,
        total_count=total,
        clean_count=total - flagged,
        flagged_count=flagged,
    )
