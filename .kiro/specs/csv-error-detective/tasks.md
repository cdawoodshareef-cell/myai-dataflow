# Implementation Plan: MyAI DataFlow — CSV Error Detective

## Overview

Maintain and improve the existing browser-based Python application built with Streamlit.

The application supports CSV validation, invoice calculation validation, supplier-wise reconciliation, JSON sales validation, and downloadable reports.

The implementation uses separate Python modules for reading, validation, reconciliation, exporting, and user-interface orchestration.

This plan distinguishes completed implementation work from outstanding verification and future improvements.

## Tasks

- [x] 1. Environment setup and dependency verification
  - Create and use a Python virtual environment.
  - Verify Python 3.14.8.
  - Maintain pinned dependencies in `requirements.txt`.
  - Verify Streamlit, pytest, and Hypothesis installation.
  - Use the project virtual environment when running tests.
  - _Status: Previously completed and verified._

- [x] 2. Project scaffold
  - Maintain the project structure and application modules.
  - Maintain the `tests/` directory and test modules.
  - Maintain `requirements.txt`.
  - Preserve the existing project and backup files.
  - _Status: Completed._

- [x] 3. Bundled sample CSV
  - Maintain `sample_data.csv`.
  - Include the eight required invoice columns:
    - Invoice Number
    - Invoice Date
    - Supplier Name
    - Product Code
    - Product Description
    - Quantity
    - Unit Price
    - Total Amount
  - Include valid, missing-value, and duplicate examples.
  - _Status: Completed. Sample workflow previously demonstrated._

- [x] 4. Implement CSV reading and unit tests
  - [x] 4.1 Implement `read_csv()` in `csv_reader.py`.
    - Read UTF-8 CSV data.
    - Return column names and data rows.
    - Handle empty files, header-only files, invalid UTF-8, and malformed input.
    - Preserve original cell values.
  - [x] 4.2 Maintain CSV reader unit tests.
    - Test valid CSV input.
    - Test empty and header-only files.
    - Test malformed input and UTF-8 behavior.

- [x] 5. Implement CSV validation and unit tests
  - [x] 5.1 Maintain validation data structures in `validator.py`.
    - `FlaggedRow`:
      - `row_number`
      - `row_values`
      - `reason`
      - `duplicate_of_row`
    - `ValidationResult`:
      - `clean_rows`
      - `flagged_rows`
      - `total_count`
      - `clean_count`
      - `flagged_count`
    - Maintain the `REQUIRED_COLUMNS` constant.
  - [x] 5.2 Implement `validate_rows()`.
    - Check required columns.
    - Detect blank and whitespace-only required values.
    - Handle short rows without raising `IndexError`.
    - Detect exact duplicate rows.
    - Preserve the first occurrence as the duplicate reference.
    - Record the first occurrence even when it has another validation issue.
    - Combine applicable validation reasons.
    - Validate invoice amounts when the required values are available.
    - Maintain the count invariant:
      `total_count = clean_count + flagged_count`.
  - [x] 5.3 Maintain core validator unit tests.
    - Missing required headers.
    - Single and multiple missing values.
    - Valid duplicate rows.
    - First occurrence with missing values.
    - Clean rows and all-flagged cases.
  - [x] 5.4 Maintain the three-identical-rows unit test.
    - Verify that the first occurrence is retained.
    - Verify that subsequent occurrences reference the first occurrence.
  - [x] 5.5 Maintain the duplicate-with-missing-value test.
    - Verify combined reason formatting.
    - Verify the duplicate reference points to the first occurrence.
  - [x] 5.6 Maintain the short-row test.
    - Verify missing required values are detected.
    - Verify no `IndexError` occurs.

- [x] 6. Implement report exporters and unit tests
  - [x] 6.1 Implement `generate_clean_csv()`.
    - Preserve the original header.
    - Include clean rows in their original order.
    - Generate UTF-8 bytes in memory.
  - [x] 6.2 Implement `generate_review_report()`.
    - Preserve original row values.
    - Pad short rows to the original header width.
    - Append these four columns:
      1. `Original Row Number`
      2. `Flag Reason`
      3. `Excel Row Number`
      4. `Duplicate of Excel Row`
    - Calculate Excel row numbers by adding one to the data-row number.
    - Preserve the first-occurrence reference for duplicate records.
    - Generate UTF-8 bytes in memory.
  - [x] 6.3 Maintain exporter unit tests.
    - Test clean CSV output.
    - Test all four additional review report columns.
    - Test row ordering.
    - Test empty reports.
    - Test short-row padding.
    - Verify review report rows have `len(column_names) + 4` fields.

- [x] 7. Implement the Streamlit application
  - [x] 7.1 Implement CSV upload and sample-data loading.
  - [x] 7.2 Implement CSV parsing, validation, and result summaries.
  - [x] 7.3 Implement flagged-row display and clean/review downloads.
  - [x] 7.4 Implement invoice calculation validation.
  - [x] 7.5 Implement supplier-wise reconciliation.
  - [x] 7.6 Implement JSON sales-data validation and downloadable results.
  - [x] 7.7 Maintain the 50 MB CSV upload limit and user-facing error handling.
  - _Status: Existing workflows implemented and previously demonstrated._

- [x] 8. Checkpoint — run core unit tests
  - Run the relevant CSV reader, validator, and exporter unit tests.
  - Resolve failures before proceeding.
  - _Status: Core unit-test checkpoint completed; the latest full-suite result is recorded in Task 10._

- [x] 9. Implement property-based tests
  - [x] 9.1 Properties P1–P5 in `tests/test_properties.py`.
    - P1: UTF-8 round-trip preservation.
    - P2: Whitespace-only cell detection.
    - P3: Missing-column completeness.
    - P4: 1-based row numbering.
    - P5: Duplicate-only reason for valid duplicates.
      - The duplicate reason must reference the generated first-occurrence row, not assume row 1.
  - [x] 9.2 Properties P6–P10.
    - P6: Missing-only reason format.
    - P7: Combined reason format.
    - P8: Combined reason references first occurrence.
    - P9: Three identical rows; later duplicates reference the generated first occurrence.
    - P10: Short-row missing-value detection.
  - [x] 9.3 Properties P11–P14.
    - P11: Count invariant.
    - P12: Review report ordering.
    - P13: Duplicate-free clean output; each complete row value sequence occurs at most once.
    - P14: Review report schema consistency.
      - Expected number of fields: `len(column_names) + 4`.
  - Maintain at least 100 examples per property using Hypothesis settings.
  - _Status: All 14 property tests inspected and confirmed present; their descriptions are documented in design.md._

- [x] 10. Checkpoint — run the full test suite
  - Run the complete test suite using the project virtual environment:
    `.venv\Scripts\python.exe -m pytest tests/ -v`
  - Resolve test failures before making further releases.
  - _Status: Verified on 2026-11-26: 122 passed in 4.08 seconds using Python 3.14.8._

- [x] 11. End-to-end integration test using the sample CSV
  - [x] 11.1 Create a dedicated integration test.
    - Load `sample_data.csv`.
    - Run CSV validation.
    - Generate clean CSV and review report.
    - Verify total, clean, and flagged counts.
    - Verify the original header is preserved.
    - Verify clean and flagged records are correctly separated.
    - Verify the review report has `len(column_names) + 4` columns.
    - Run the test using the project virtual environment.
  - _Status: Completed and verified. `tests/test_sample_csv_integration.py` passes as part of the full 121-test suite._

- [x] 12. Deployment verification
  - [x] 12.1 Local Windows UI smoke test.
    - Start Streamlit using the project's virtual environment.
    - Open the local application.
    - Upload `sample_data.csv`.
    - Verify the results summary and flagged-row table.
    - Download and inspect the clean CSV, review report, and reconciliation report.
    - Verify the downloaded files are valid and non-empty.
    - Upload a JSON array and a single JSON object; verify validation results and the downloadable report.
    - Verify malformed JSON is handled without crashing the application.
    - Verify CSV and JSON uploaders display the configured 50 MB limit.
    - _Status: Completed and manually verified on 2026-11-25._
  - [x] 12.2 Streamlit Community Cloud deployment configuration.
    - Verify `requirements.txt` is present.
    - Verify `sample_data.csv` is available to the application.
    - Verify sample-data loading uses a path relative to the application file.
    - Verify the deployment configuration.
    - _Status: Previously verified._

## Additional Application Modules

The following modules are part of the existing application and should remain covered by the test suite:

- `invoice_validator.py`: Decimal-based invoice calculation validation.
- `reconciliation_report.py`: Supplier-wise reconciliation.
- `json_validator.py`: JSON sales-data validation.
- `currency_validator.py`: Standalone currency validation module; not currently integrated into the main dashboard.

## Quality and Data Integrity Rules

1. Preserve original source records.
2. Keep duplicate references traceable to the first occurrence.
3. Keep flagged and clean records separate.
4. Preserve original row numbering.
5. Include understandable validation reasons.
6. Use decimal arithmetic for invoice calculations.
7. Exclude duplicate records from reconciliation totals.
8. Do not silently discard invalid invoices from reconciliation totals.
9. Maintain accurate export column counts.
10. Add tests when new functionality is introduced.

## Outstanding Work

1. Re-run the complete test suite after future changes.
2. Measure actual code coverage before claiming a coverage percentage.
3. Consider currency-validator dashboard integration as a separate future feature.

## Notes

- Completed task descriptions have been updated to match the existing implementation.
- A checked task means the work has been completed and previously verified; it does not guarantee future changes will continue to pass.
- Unverified work must remain unchecked.
- The original task document is preserved in `tasks.md.before_update_20261125`.
- Future implementation changes should follow the approved requirements and design documents.

## Task Dependency Graph

```text
Environment and project setup
             |
             v
      CSV reader and tests
             |
             v
       CSV validation
             |
             v
       Exporters and tests
             |
             v
       Streamlit workflows
             |
             v
     Property-based tests
             |
             v
       Full test suite
             |
             v
  Sample-data integration test
             |
             v
       Deployment checks
```

**End of Implementation Plan**