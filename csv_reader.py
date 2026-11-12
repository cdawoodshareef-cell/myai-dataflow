"""csv_reader.py — CSV parsing and header extraction."""
from __future__ import annotations
import csv
import io
from typing import List, Tuple


def read_csv(file_obj) -> Tuple[List[str], List[List[str]]]:
    """Read a CSV file object and return (column_names, data_rows).

    Args:
        file_obj: A file-like object (bytes or text, UTF-8).

    Returns:
        Tuple of (column_names, data_rows) where column_names is a list of
        strings and data_rows is a list of lists of strings.

    Raises:
        ValueError: If the file is empty, has no header, has no data rows, or
                    if any data row contains more fields than the header row.
    """
    # Normalise input: bytes/BytesIO → TextIOWrapper, text file-like → use as-is
    if isinstance(file_obj, (bytes, bytearray)):
        file_obj = io.BytesIO(file_obj)

    if hasattr(file_obj, "read"):
        # Peek at what read() returns to decide whether we need to decode
        sample = file_obj.read(0)
        file_obj.seek(0)
        if isinstance(sample, bytes):
            # Binary stream — wrap with UTF-8 text decoder
            try:
                text_stream = io.TextIOWrapper(file_obj, encoding="utf-8")
                rows = list(csv.reader(text_stream))
            except UnicodeDecodeError:
                raise ValueError(
                    "File encoding is not supported. Please upload a UTF-8 encoded CSV."
                )
        else:
            # Already a text stream
            try:
                rows = list(csv.reader(file_obj))
            except UnicodeDecodeError:
                raise ValueError(
                    "File encoding is not supported. Please upload a UTF-8 encoded CSV."
                )
    else:
        raise TypeError("file_obj must be a file-like object or bytes.")

    if not rows:
        raise ValueError("The file is empty or contains no data.")

    column_names: List[str] = rows[0]
    data_rows: List[List[str]] = rows[1:]

    if not data_rows:
        raise ValueError("The file contains no data rows.")

    # Reject any data row that has more fields than the header.
    # Row numbers are 1-based, counting from the first data row (header excluded).
    expected = len(column_names)
    for row_number, row in enumerate(data_rows, start=1):
        if len(row) > expected:
            raise ValueError(
                f"Data row {row_number} has {len(row)} fields but the header has "
                f"{expected}. Please check for extra commas or unquoted values in "
                f"that row."
            )

    return column_names, data_rows
