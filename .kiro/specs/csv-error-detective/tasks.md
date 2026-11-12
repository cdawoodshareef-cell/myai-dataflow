# Implementation Plan: CSV Error Detective

## Overview

Implement a browser-based Python web application using Streamlit that validates supplier sales CSV files for missing required values and exact duplicate rows. The implementation follows the four-module architecture defined in the design document (`csv_reader.py`, `validator.py`, `exporter.py`, `app.py`) with a bundled sample CSV and comprehensive test suite (pytest unit tests + Hypothesis property-based tests).

## Tasks

- [x] 1. Environment setup and dependency verification
  - Create a fresh Python virtual environment using Python 3.14.8: `py -3.14 -m venv .venv`
  - Activate the virtual environment: `.venv\Scripts\activate`
  - Create `requirements.txt` with pinned versions: `streamlit==1.46.0`, `pytest==8.3.5`, `hypothesis==6.165.0`
  - Run `pip install -r requirements.txt`; if any pin fails to install (version not found, incompatible with Python 3.14.8), **STOP and add a comment or note documenting the exact error before changing any version pin**
  - Create a placeholder `app.py` containing only `import streamlit as st; st.write("hello")` and run `streamlit run app.py` to confirm the browser opens at `http://localhost:8501`
  - This task must be fully completed and verified before any subsequent task begins
  - _Requirements: 9.1, 9.2, 9.4, 9.5_

- [x] 2. Project scaffold
  - [x] 2.1 Create the application directory structure
    - Create the top-level `csv-error-detective/` directory with subdirectories: `tests/`
    - Create stub Python files: `app.py`, `csv_reader.py`, `validator.py`, `exporter.py`
    - Create stub test files: `tests/test_csv_reader.py`, `tests/test_validator.py`, `tests/test_exporter.py`, `tests/test_properties.py`
    - Create `tests/__init__.py` (empty)
    - Write final `requirements.txt` with pinned versions: `streamlit==1.46.0`, `pytest==8.3.5`, `hypothesis==6.165.0`
    - _Requirements: 9.4, 9.5_

- [x] 3. Create bundled sample CSV
  - [x] 3.1 Write `sample_data.csv` with 15+ data rows meeting all sample requirements
    - Include the required header row: `Invoice Number,Invoice Date,Supplier Name,Product Code,Product Description,Quantity,Unit Price,Total Amount`
    - Include at least 8 fully valid rows (no missing values, no duplicates) so they appear in Clean CSV output
    - Include at least 3 rows with one or more missing values spread across different Required_Columns (e.g., one row missing `Invoice Number`, one missing `Quantity`, one missing `Supplier Name` and `Unit Price`)
    - Include at least 2 rows that are exact duplicates of earlier rows in the file (the duplicate rows must appear after their first occurrence)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 4. Implement `csv_reader.py` and its unit tests
  - [x] 4.1 Implement `read_csv(file_obj)` in `csv_reader.py`
    - Parse the file using Python's standard-library `csv` module with UTF-8 encoding
    - Treat the first row as the header; return `(column_names: List[str], data_rows: List[List[str]])`
    - Raise `ValueError` with a descriptive message when the file is empty, has no header, or has no data rows
    - Preserve original cell values without modification
    - _Requirements: 1.3, 1.5, 1.6_

  - [x] 4.2 Write unit tests for `csv_reader.py` in `tests/test_csv_reader.py`
    - Test: valid CSV with multiple rows and UTF-8 characters returns correct column names and data rows
    - Test: empty file raises `ValueError`
    - Test: file with header only (no data rows) raises `ValueError`
    - Test: malformed CSV (e.g., unclosed quote) raises `ValueError` or returns gracefully with a descriptive error
    - _Requirements: 1.3, 1.5, 1.6_

- [x] 5. Implement `validator.py` and its unit tests
  - [x] 5.1 Define `FlaggedRow` and `ValidationResult` dataclasses in `validator.py`
    - `FlaggedRow`: fields `row_number: int`, `row_values: List[str]`, `reason: str`
    - `ValidationResult`: fields `clean_rows`, `flagged_rows`, `total_count`, `clean_count`, `flagged_count`
    - Define `REQUIRED_COLUMNS` constant list
    - _Requirements: 2.1, 3.4, 5.1_

  - [x] 5.2 Implement `validate_rows(column_names, data_rows)` in `validator.py`
    - Raise `ValueError` listing missing column names when any Required_Column is absent from `column_names`
    - Perform a single-pass O(n) traversal; maintain a `seen: Dict[Tuple[str, ...], int]` for duplicate detection
    - For each row: use index-safe access `row[i] if i < len(row) else ""` for required column checks
    - Flag missing values (empty, whitespace-only, or absent cells) with reason `"Missing value in column(s): 'ColA', 'ColB'"` (columns listed in header order)
    - Flag exact duplicates (not first occurrence) with reason `"Exact duplicate of row N"` where N is the first occurrence 1-based row number
    - For rows that are both duplicate and have missing values, combine reasons: `"Exact duplicate of row N; Missing value in column(s): 'ColA'"`
    - Register the first occurrence in `seen` before processing subsequent rows; first occurrences with missing values are flagged for missing values only, NOT as duplicates
    - Flagged rows are never added to `clean_rows`
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 5.3 Write unit tests for `validator.py` — core validation cases in `tests/test_validator.py`
    - Test: missing required column in header raises `ValueError` listing the absent column name
    - Test: single missing value in one required column — row is flagged with correct single-column reason string
    - Test: multiple missing values in one row — all column names appear in the reason string in header order
    - Test: first occurrence of a fully valid duplicate row appears in clean output; second occurrence is flagged with duplicate reason
    - Test: first occurrence of a row with missing values is flagged for missing values only, NOT marked as duplicate
    - Test: row with no issues (not missing, not duplicate) appears in clean output only
    - Test: all rows valid — `flagged_count == 0`, `clean_count == total_count`
    - Test: all rows flagged — clean output is empty, `flagged_count == total_count`
    - _Requirements: 2.2, 3.1, 3.2, 3.3, 4.1, 4.2, 4.4, 4.5, 5.1_

  - [x] 5.4 Write unit test: **Three-Identical-Rows at positions 4, 5, 6** in `tests/test_validator.py`
    - Input: a CSV where data rows 1–3 are distinct valid rows and data rows 4, 5, and 6 are identical and fully valid (no missing values)
    - Expected: row 4 (first occurrence) is included in the clean output
    - Expected: row 5 is flagged with reason `"Exact duplicate of row 4"`
    - Expected: row 6 is flagged with reason `"Exact duplicate of row 4"` (references row 4, NOT row 5)
    - This is a concrete unit test with fixed row numbers, distinct from property test P9
    - _Requirements: 4.2, 4.3_

  - [x] 5.5 Write unit test: **Duplicate with Missing Value** in `tests/test_validator.py`
    - Input: a valid row at position p1; a subsequent row at position p2 identical to p1 except it also has at least one missing required value
    - Expected: p2 is flagged with both reasons joined by `"; "`, duplicate reason first: `"Exact duplicate of row <p1>; Missing value in column(s): 'ColX'"`
    - Expected: the row number in the duplicate reason correctly references p1 (the first occurrence), not p2
    - This test must remain its own distinct test case, not merged with the three-identical-rows test
    - _Requirements: 4.6, 5.3_

  - [x] 5.6 Write unit test: short-row (fewer fields than header) in `tests/test_validator.py`
    - Input: a row with fewer fields than the header, where absent fields correspond to required columns
    - Expected: row is flagged for the missing required columns it is short on
    - Expected: no `IndexError` is raised
    - _Requirements: 2.3_

- [x] 6. Implement `exporter.py` and its unit tests
  - [x] 6.1 Implement `generate_clean_csv(column_names, clean_rows)` in `exporter.py`
    - Build output entirely in memory using `io.StringIO` + `csv.writer`
    - First row is the original header; subsequent rows are the clean data rows in original order
    - Return UTF-8 encoded bytes: `sio.getvalue().encode('utf-8')`
    - No files written to disk
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.2 Implement `generate_review_report(column_names, flagged_rows)` in `exporter.py`
    - Build output entirely in memory using `io.StringIO` + `csv.writer`
    - Header: `column_names + ["Original Row Number", "Flag Reason"]`
    - For each `FlaggedRow`: pad `row_values` with empty strings to `len(column_names)` if shorter, then append `row_number` and `reason`
    - Return UTF-8 encoded bytes
    - No files written to disk
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 6.3 Write unit tests for `exporter.py` in `tests/test_exporter.py`
    - Test: clean CSV output has correct header and all clean rows; no flagged rows present
    - Test: review report header includes `Original Row Number` and `Flag Reason` as last two columns
    - Test: review report rows list flagged rows in ascending row number order
    - Test: empty clean output (zero clean rows) contains only the header row
    - Test: empty review report (zero flagged rows) contains only the header row
    - Test: short-row padding — a `FlaggedRow` with fewer values than `column_names` is padded with empty strings so the output row has exactly `len(column_names) + 2` fields
    - _Requirements: 6.2, 6.3, 6.6, 7.2, 7.3, 7.4, 7.6_

- [x] 7. Implement `app.py` Streamlit UI
  - [x] 7.1 Implement the Streamlit UI layout and file upload in `app.py`
    - Display application title and brief description
    - Render `st.file_uploader()` accepting `.csv` files only; display error `"Only CSV files are accepted."` for non-CSV uploads
    - Provide a "Load Sample CSV" button that reads `sample_data.csv` from the application root directory
    - _Requirements: 1.1, 1.2, 8.6_

  - [x] 7.2 Implement the validation workflow trigger in `app.py`
    - On file upload or sample load: call `csv_reader.read_csv()` to parse the file
    - On parse success: call `validator.validate_rows()` to validate
    - On validation complete: display summary counts — total rows processed, clean rows, flagged rows
    - On parse or validation error: display the descriptive error message and halt processing (allow re-upload)
    - _Requirements: 1.3, 1.4, 1.6, 2.2, 5.1_

  - [x] 7.3 Implement the results display and download buttons in `app.py`
    - Display flagged rows in a table sorted by ascending original row number, showing: row number, all original cell values, and the reason
    - Render `st.download_button()` for Clean CSV (`filename="clean_output.csv"`, `mime="text/csv"`) using `exporter.generate_clean_csv()`
    - Render `st.download_button()` for Review Report (`filename="review_report.csv"`, `mime="text/csv"`) using `exporter.generate_review_report()`
    - If all rows are flagged, display notice `"No clean rows found."` alongside the header-only clean CSV download
    - If no rows are flagged, display notice `"No flagged rows found."` alongside the header-only review report download
    - _Requirements: 5.2, 5.4, 6.1, 6.5, 6.6, 7.1, 7.5, 7.6_

- [x] 8. Checkpoint — run all unit tests
  - Run `pytest tests/test_csv_reader.py tests/test_validator.py tests/test_exporter.py -v` and confirm all tests pass
  - Fix any failures before proceeding to property-based tests
  - Ensure all tests pass; ask the user if questions arise.

- [ ] 9. Implement property-based tests
  - [x] 9.1 Write property tests P1–P5 in `tests/test_properties.py`
    - **Property 1: UTF-8 Round-Trip Preservation** — Generate arbitrary rows of string values, encode as UTF-8 CSV via `exporter`, read back via `csv_reader`, verify values are identical. `# Feature: csv-error-detective, Property 1: UTF-8 Round-Trip Preservation`
    - **Property 2: Whitespace-Only Cell Detection** — Generate strings composed entirely of whitespace characters; pass as cell values in required columns; verify validator flags them as missing values. `# Feature: csv-error-detective, Property 2: Whitespace-Only Cell Detection`
    - **Property 3: Missing Column Completeness** — Generate rows missing any non-empty subset of required columns; verify the reason string names all missing columns in header order. `# Feature: csv-error-detective, Property 3: Missing Column Completeness`
    - **Property 4: 1-Based Row Numbering** — Generate any flagged row as the first data row (after the header); verify its `row_number` is 1. `# Feature: csv-error-detective, Property 4: 1-Based Row Numbering`
    - **Property 5: Duplicate-Only Reason for Valid Duplicates** — Generate two identical valid rows at positions p1 < p2; verify p1 is in clean output and p2 is flagged with reason `"Exact duplicate of row 1"`. `# Feature: csv-error-detective, Property 5: Duplicate-Only Reason for Valid Duplicates`
    - Minimum 100 iterations per property (`@settings(max_examples=100)`)
    - _Requirements: 1.3, 2.3, 3.2, 3.3, 3.4, 4.2, 4.4_

  - [ ] 9.2 Write property tests P6–P10 in `tests/test_properties.py`
    - **Property 6: Missing-Only Reason Format** — Generate a row with exactly one missing required value and no duplicates; verify reason is exactly `"Missing value in column(s): 'ColName'"`. `# Feature: csv-error-detective, Property 6: Missing-Only Reason Format`
    - **Property 7: Combined Reason Format** — Generate a valid row and a duplicate of it with a missing value; verify combined reason format `"Exact duplicate of row N; Missing value in column(s): 'ColA'"`. `# Feature: csv-error-detective, Property 7: Combined Reason Format for Duplicate with Missing Values`
    - **Property 8: Combined Reason References First Occurrence** — Generate a duplicate with missing values after multiple prior occurrences; verify row number N in the duplicate reason references the first occurrence only. `# Feature: csv-error-detective, Property 8: Combined Reason References First Occurrence`
    - **Property 9: Three Identical Rows — First Occurrence Rule** — Generate three identical valid rows at positions p1 < p2 < p3; verify clean output contains exactly one copy (p1) and both p2 and p3 are flagged referencing p1. `# Feature: csv-error-detective, Property 9: Three Identical Rows — First Occurrence Rule`
    - **Property 10: Short Row Missing Value Detection** — Generate a row with fewer fields than the header where absent fields cover required columns; verify flagged for those columns with no `IndexError`. `# Feature: csv-error-detective, Property 10: Short Row Missing Value Detection`
    - Minimum 100 iterations per property
    - _Requirements: 2.3, 3.2, 4.2, 4.3, 4.6, 5.3_

  - [ ] 9.3 Write property tests P11–P14 in `tests/test_properties.py`
    - **Property 11: Count Invariant** — For any set of input rows, verify `clean_count + flagged_count == total_count`. `# Feature: csv-error-detective, Property 11: Count Invariant`
    - **Property 12: Sort Order of Flagged Rows** — Generate flagged rows in any order; verify the review report lists them in ascending row number order. `# Feature: csv-error-detective, Property 12: Sort Order of Flagged Rows`
    - **Property 13: Clean Output Integrity** — For any input, verify no row that appears in the review report (flagged rows) also appears in the clean CSV output. `# Feature: csv-error-detective, Property 13: Clean Output Integrity`
    - **Property 14: Review Report Schema Consistency** — For any flagged row, verify the corresponding row in the review report has exactly `len(column_names) + 2` fields. `# Feature: csv-error-detective, Property 14: Review Report Schema Consistency`
    - Minimum 100 iterations per property
    - _Requirements: 4.7, 5.1, 5.4, 6.3, 7.2, 7.3, 7.4_

- [ ] 10. Checkpoint — run full test suite
  - Run `pytest tests/ -v` and confirm all unit tests and property-based tests pass
  - Ensure all tests pass; ask the user if questions arise.

- [ ] 11. End-to-end integration test using the sample CSV
  - [ ] 11.1 Write an integration test in `tests/test_exporter.py` (or a new `tests/test_integration.py`) that exercises the complete workflow
    - Load `sample_data.csv` via `csv_reader.read_csv()`
    - Run `validator.validate_rows()` on the parsed data
    - Call `exporter.generate_clean_csv()` and `exporter.generate_review_report()`
    - Assert: `total_count` equals the number of data rows in `sample_data.csv`
    - Assert: `clean_count + flagged_count == total_count`
    - Assert: clean CSV bytes decode to a valid CSV whose first row matches the original header
    - Assert: review report CSV bytes decode to a valid CSV with `len(original_columns) + 2` columns
    - Assert: all rows in the sample that were fully valid and non-duplicate appear in the clean CSV
    - Assert: all rows in the sample that have missing values or are duplicates appear in the review report
    - _Requirements: 5.1, 6.1, 6.2, 6.3, 7.1, 7.2, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 12. Deployment verification
  - [ ] 12.1 Local Windows deployment smoke test
    - With the virtual environment activated, run `streamlit run app.py` from the `csv-error-detective/` directory
    - Confirm the application opens at `http://localhost:8501` without errors
    - Upload `sample_data.csv` via the UI; confirm the results summary, flagged row table, and both download buttons appear
    - Download both output files and verify they are valid non-empty CSV files
    - _Requirements: 9.1, 9.2, 9.3, 9.6_

  - [ ] 12.2 Verify Streamlit Community Cloud deployment compatibility
    - Confirm `requirements.txt` is present in the repository root with all three pinned dependencies
    - Confirm `sample_data.csv` is present in the repository root (not excluded by `.gitignore`)
    - Confirm `app.py` reads `sample_data.csv` using a path relative to the script file (e.g., `Path(__file__).parent / "sample_data.csv"`) so it resolves correctly when deployed to Streamlit Community Cloud
    - _Requirements: 9.6_

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints (tasks 8 and 10) ensure incremental validation
- Property tests validate universal correctness properties across all 14 properties defined in the design
- Unit tests validate specific examples and edge cases
- The three-identical-rows unit test (task 5.4) and the duplicate-with-missing-value unit test (task 5.5) are **distinct** concrete tests and must not be merged
- The environment setup task (task 1) is a **blocking prerequisite** — do not proceed to task 2 until it is fully verified
- If any pinned dependency fails to install on Python 3.14.8, document the error before changing any version

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["2.1"] },
    { "id": 1, "tasks": ["3.1"] },
    { "id": 2, "tasks": ["4.1"] },
    { "id": 3, "tasks": ["4.2", "5.1"] },
    { "id": 4, "tasks": ["5.2"] },
    { "id": 5, "tasks": ["5.3", "5.4", "5.5", "5.6", "6.1"] },
    { "id": 6, "tasks": ["6.2", "6.3"] },
    { "id": 7, "tasks": ["7.1"] },
    { "id": 8, "tasks": ["7.2"] },
    { "id": 9, "tasks": ["7.3", "9.1"] },
    { "id": 10, "tasks": ["9.2", "9.3"] },
    { "id": 11, "tasks": ["11.1"] },
    { "id": 12, "tasks": ["12.1", "12.2"] }
  ]
}
```
