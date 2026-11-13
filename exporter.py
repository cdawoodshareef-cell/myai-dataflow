"""exporter.py — In-memory CSV output generation."""
from __future__ import annotations
import csv
import io
from typing import List

from validator import FlaggedRow


def generate_clean_csv(
    column_names: List[str],
    clean_rows: List[List[str]],
) -> bytes:
    """Build the Clean CSV in memory and return UTF-8 bytes.

    Args:
        column_names: Header column names.
        clean_rows: Rows that passed all validation checks.

    Returns:
        UTF-8 encoded bytes of the clean CSV.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(column_names)
    writer.writerows(clean_rows)
    return buf.getvalue().encode("utf-8")


def generate_review_report(
    column_names: List[str],
    flagged_rows: List[FlaggedRow],
) -> bytes:
    """Build the Review Report CSV in memory and return UTF-8 bytes.

    The report header is the original columns plus 'Original Row Number'
    and 'Flag Reason' appended at the end.

    For each flagged row, row_values is padded with empty strings to exactly
    len(column_names) fields (handles short rows) before appending the row
    number and reason. This keeps 'Original Row Number' and 'Flag Reason'
    under the correct headers regardless of how many fields the original row had.

    Args:
        column_names: Original header column names.
        flagged_rows: Rows that were flagged during validation.

    Returns:
        UTF-8 encoded bytes of the review report CSV.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(column_names + [
        "Original Row Number",
        "Flag Reason",
        "Excel Row Number",
        "Duplicate of Excel Row",
    ])
    for fr in flagged_rows:
        # Pad short rows; truncate over-wide rows to column width
        padded = list(fr.row_values) + [""] * max(0, len(column_names) - len(fr.row_values))
        padded = padded[: len(column_names)]
        duplicate_excel_row = (
            fr.duplicate_of_row + 1 if fr.duplicate_of_row is not None else ""
        )
        writer.writerow(padded + [
            fr.row_number,
            fr.reason,
            fr.row_number + 1,
            duplicate_excel_row,
        ])
    return buf.getvalue().encode("utf-8")
