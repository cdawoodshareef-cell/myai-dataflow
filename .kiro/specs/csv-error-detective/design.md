# Design Document

## MyAI DataFlow — CSV Error Detective

**Status:** Current implementation
**Specification:** CSV Error Detective
**Project:** MyAI DataFlow

---

## 1. Introduction

MyAI DataFlow is a browser-based Python application built with Streamlit to help small businesses and wholesalers inspect sales and invoice data.

The application supports several related data-quality workflows:

1. CSV file reading and validation.
2. Missing-value detection.
3. Exact duplicate-row detection.
4. Invoice amount validation.
5. Clean CSV export.
6. Review report generation.
7. Supplier-wise financial reconciliation.
8. JSON sales-data validation and reporting.

The application separates data reading, validation, reporting, and user-interface responsibilities into Python modules.

The purpose of this design is to describe the existing application architecture and its implemented behavior accurately.

## 2. Architecture Overview

### 2.1 Application Modules

The application uses eight active Python modules:

| Module | Responsibility |
|---|---|
| `app.py` | Streamlit user interface and workflow orchestration |
| `csv_reader.py` | Reads and checks uploaded CSV files |
| `validator.py` | Performs CSV row validation and identifies flagged records |
| `invoice_validator.py` | Validates invoice calculations using decimal arithmetic |
| `currency_validator.py` | Provides standalone currency validation functionality |
| `json_validator.py` | Validates JSON sales data |
| `reconciliation_report.py` | Calculates supplier-wise reconciliation results |
| `exporter.py` | Generates downloadable CSV reports |

The currency validator is a standalone module. It is not currently integrated into the main application workflow.

### 2.2 High-Level Architecture

The application follows this general structure:

```text
                 USER
                   |
                   v
             STREAMLIT UI
                app.py
                   |
       +-----------+-----------+
       |           |           |
       v           v           v
    CSV Flow   Invoice Flow  JSON Flow
       |           |           |
       v           v           v
 csv_reader.py invoice_validator.py json_validator.py
       |
       v
  validator.py
       |
       +----------------------+
       |                      |
       v                      v
 Clean / Flagged Rows   Reconciliation
       |                reconciliation_report.py
       |                      |
       +----------+-----------+
                  |
                  v
              exporter.py
                  |
                  v
        Downloadable Reports
```

The diagram represents the main responsibilities and relationships. The standalone currency validator is not part of the integrated workflow.

## 3. Data Input

### 3.1 CSV Upload

The application accepts CSV uploads through the Streamlit interface.

The current upload limit is 50 MB.

The CSV reader supports:
- Byte input.
- Bytearray input.
- File-like input.
- UTF-8 decoding.
- Empty-file detection.
- Header-only file detection.
- Rows containing more values than the header.

Short rows are allowed through the reader so that the validator can identify missing values.

### 3.2 Required Invoice Columns

The invoice validation workflow expects these eight columns:

1. Invoice Number
2. Invoice Date
3. Supplier Name
4. Product Code
5. Product Description
6. Quantity
7. Unit Price
8. Total Amount

Header matching is case-insensitive and ignores surrounding whitespace.

A missing required column prevents normal validation of the uploaded invoice data.

### 3.3 Bundled Sample Data

The application includes `sample_data.csv`.

The application locates this file relative to `app.py`, using the project directory rather than relying on the current working directory.

The sample file provides a demonstration dataset for the application.

## 4. CSV Validation

### 4.1 Validation Data Structures

The CSV validation module uses two main result structures.

#### FlaggedRow

A flagged record contains:

- `row_number`: Original data-row number, excluding the header.
- `row_values`: Original cell values.
- `reason`: Explanation of why the row was flagged.
- `duplicate_of_row`: Reference to the first occurrence when the row is a duplicate.

#### ValidationResult

The validation result contains:

- `clean_rows`
- `flagged_rows`
- `total_count`
- `clean_count`
- `flagged_count`

The expected count relationship is:

```text
total_count = clean_count + flagged_count
```

### 4.2 Missing-Value Detection

The validator checks required data values.

A value is considered missing when it is blank or contains only whitespace.

Short rows are also checked for missing values.

Rows with missing required information are flagged for review.

### 4.3 Exact Duplicate Detection

The validator detects exact duplicate rows using their complete row values.

The first occurrence is retained as the reference record.

Subsequent matching rows are flagged as duplicates.

The `duplicate_of_row` field identifies the first occurrence.

The first occurrence is recorded even if that row has another validation problem.

Duplicate detection does not mean that similar-looking records are duplicates. The current implementation checks exact row equality.

### 4.4 Invoice Amount Validation

The CSV validator checks invoice amounts when Quantity, Unit Price, and Total Amount are available.

Rows with an invalid invoice amount receive the reason:

```text
Invalid invoice amount
```

A row can have multiple reasons, such as missing values and duplicate status.

### 4.5 Clean and Flagged Records

The validator separates records into:

- Clean rows: Records that pass the applicable checks.
- Flagged rows: Records requiring review.

The application does not silently discard flagged records. It makes them available in the review workflow.

## 5. Invoice Calculation Validation

The `invoice_validator.py` module performs invoice arithmetic validation.

### 5.1 Calculation

The expected invoice amount is calculated using:

```text
Expected Total = Quantity × Unit Price
```

The implementation uses Python's `Decimal` arithmetic rather than ordinary binary floating-point arithmetic.

### 5.2 Validation Rules

The invoice calculation checks:

- Quantity is present and numeric.
- Unit Price is present and numeric.
- Total Amount is present and numeric.
- Values are finite.
- Quantity is greater than zero.
- Unit Price is greater than zero.
- The calculated total matches the reported total after rounding.

The calculated amount is rounded to two decimal places using `ROUND_HALF_UP`.

### 5.3 Example

```text
Quantity:       3
Unit Price:     0.335
Expected Total: 1.01
```

This example demonstrates the two-decimal rounding behavior.

Invalid, missing, nonnumeric, or non-finite values are handled as validation failures.

## 6. Supplier-Wise Reconciliation

The `reconciliation_report.py` module calculates supplier-wise invoice reconciliation information.

### 6.1 Purpose

The reconciliation workflow helps users compare invoice records and financial totals by supplier.

### 6.2 Processing Rules

The implementation:

- Groups records by supplier.
- Calculates invoice-related counts and financial totals.
- Excludes duplicate records from reconciliation totals.
- Does not automatically remove invalid invoices from financial totals.
- Handles missing required headers and missing invoice numbers.

This distinction is important: duplicate exclusion and invoice validity are separate considerations.

### 6.3 Dashboard Output

The application displays reconciliation information, including:

- Invoice counts.
- Valid and invalid invoice counts.
- Duplicate exclusions.
- Financial totals.
- Supplier-wise results.

The reconciliation results can also be exported as a CSV file.

## 7. JSON Sales Validation

The `json_validator.py` module provides a separate JSON validation workflow.

### 7.1 Supported Validation

The current sales validator checks whether the supplied JSON:

1. Can be parsed.
2. Contains a JSON object.
3. Contains a `sales` field.
4. Has a numeric sales value.
5. Does not contain a negative sales value.

The validator returns a status such as:

```text
VALID
```

or an explanatory invalid status.

### 7.2 Record Processing

The application also supports processing JSON records and producing row/status results.

The interface displays validation counts and a results table.

The results can be downloaded as a CSV report.

### 7.3 Scope Limitation

This is a narrow sales-field validator.

It is not a general-purpose JSON Schema validation engine and does not currently validate arbitrary JSON structures against user-defined schemas.

## 8. Report Generation and Export

The `exporter.py` module generates downloadable reports.

### 8.1 Clean CSV

The clean CSV export:

- Preserves the original header.
- Contains clean rows.
- Uses UTF-8 encoding.
- Is returned as downloadable bytes.

### 8.2 Review Report

The review report contains the original row data and four additional columns:

1. `Original Row Number`
2. `Flag Reason`
3. `Excel Row Number`
4. `Duplicate of Excel Row`

The Excel row number is calculated as:

```text
Excel Row Number = Original Row Number + 1
```

The additional one accounts for the header row.

For duplicate records:

```text
Duplicate of Excel Row = Duplicate Reference Row + 1
```

When a record is not a duplicate, the duplicate reference is left empty.

Short rows are padded so the exported report has a consistent number of columns.

### 8.3 Reconciliation CSV

The exporter also generates a downloadable supplier reconciliation CSV.

### 8.4 JSON Report

The Streamlit interface provides a downloadable JSON validation report.

## 9. Streamlit User Interface

The `app.py` module coordinates the application's user-facing workflows.

The interface includes:

- CSV file upload.
- CSV validation results.
- Clean and flagged record counts.
- Clean CSV download.
- Review report download.
- Invoice validation and reconciliation information.
- Supplier-wise reconciliation results.
- JSON sales-data validation.
- Downloadable validation reports.

The UI is responsible for presenting results and connecting the individual processing modules.

Validation logic should remain in the relevant modules rather than being unnecessarily duplicated in the interface.

## 10. Error Handling

The application handles common input and validation problems.

### 10.1 CSV Errors

Examples include:

- Empty file.
- Header-only file.
- Invalid UTF-8 content.
- Missing required columns.
- Rows with too many values.
- Missing cell values.

### 10.2 Invoice Errors

Examples include:

- Missing numeric values.
- Nonnumeric values.
- Non-finite values.
- Zero or negative quantity.
- Zero or negative unit price.
- Incorrect invoice totals.

### 10.3 JSON Errors

Examples include:

- Invalid JSON syntax.
- JSON values that are not objects.
- Missing sales field.
- Nonnumeric sales values.
- Negative sales values.

Errors should be communicated clearly so that users can correct their source data.

## 11. Testing Strategy

The project uses pytest and Hypothesis.

The test suite covers the principal data-processing modules.

### 11.1 Unit Tests

Testing includes:

- CSV reading.
- CSV validation.
- Invoice validation.
- Currency validation.
- JSON validation.
- Supplier reconciliation.
- CSV report generation.

### 11.2 Property-Based Tests

The project includes property-based tests in:

```text
tests/test_properties.py
```

The test suite contains 14 property tests (P1-P14). Each property test is configured with up to 100 generated examples.

The properties cover important validation behavior, including record counts, missing values, duplicates, and report generation.

Property descriptions must reflect actual implementation behavior.

In particular:

- Duplicate references must point to the actual first occurrence, not assume that the first occurrence is always row 1.
- Review report column-count expectations must account for four additional columns.

#### Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

##### Property 1: UTF-8 Round-Trip Preservation

*For any* generated rows containing safe string values, encoding those rows as UTF-8 CSV and reading them with `csv_reader.read_csv()` SHALL preserve the column names and all cell values exactly.

**Validates: Requirement 1.3**

---

##### Property 2: Whitespace-Only Cell Detection

*For any* required cell containing only spaces or tabs, the validator SHALL flag the row as containing a missing value and identify the affected column in the reason.

**Validates: Requirements 2.4, 3.1**

---

##### Property 3: Missing Column Completeness

*For any* row with one or more missing required values, the validator SHALL include every affected column name in the reason, in header order.

**Validates: Requirements 3.3, 3.4**

---

##### Property 4: 1-Based Row Numbering

*For any* single data row that is flagged, the validator SHALL assign it original data row number 1, excluding the header.

**Validates: Requirement 3.5**

---

##### Property 5: Duplicate-Only Reason for Valid Duplicates

*For any* valid row supplied twice consecutively, the validator SHALL retain the first occurrence in the clean output and flag the second occurrence with the exact reason `Exact duplicate of row 1`.

**Validates: Requirements 4.2, 4.3, 4.4, 4.5, 7.3**

---

##### Property 6: Missing-Only Reason Format

*For any* otherwise valid row with exactly one required value replaced by an empty string, the validator SHALL produce the exact reason format `Missing value in column(s): ColName`, with the column name enclosed in single quotes in the actual reason.

**Validates: Requirements 3.2, 3.3**

---

##### Property 7: Combined Reason Format for Duplicate with Missing Values

*For any* first occurrence with a missing required value followed by an identical row, the validator SHALL flag the later row with the duplicate reason first, followed by `; ` and the missing-value reason.

**Validates: Requirement 4.7**

---

##### Property 8: Combined Reason References First Occurrence

*For any* duplicate group preceded by distinct valid padding rows, the duplicate portion of the combined reason SHALL reference the actual 1-based row number of the group first occurrence, not row 1 or the current duplicate row.

**Validates: Requirement 4.4**

---

##### Property 9: Three Identical Rows — First Occurrence Rule

*For any* three identical valid rows preceded by distinct valid rows, the clean output SHALL contain exactly one copy, and both subsequent duplicate reasons SHALL reference the first occurrence actual row number.

**Validates: Requirements 4.2, 4.3, 4.4, 4.5, 4.8**

---

##### Property 10: Short Row Missing Value Detection

*For any* row containing fewer fields than the required header, the validator SHALL flag the row, identify the required columns absent because of the short row, and SHALL NOT raise an `IndexError`.

**Validates: Requirement 2.5**

---

##### Property 11: Count Invariant

*For any* set of input rows, the validator SHALL maintain `clean_count + flagged_count == total_count`, and `total_count` SHALL equal the number of input rows.

**Validates: Requirements 6.1, 6.2, 6.3, 6.7**

---

##### Property 12: Sort Order of Flagged Rows

*For any* generated set of input rows that produces flagged records, the review report SHALL list those records in ascending original row-number order.

**Validates: Requirements 6.5, 8.10**

---

##### Property 13: Duplicate-Free Clean Output

*For any* generated input rows, the clean output SHALL contain no repeated row values; each complete row value sequence SHALL occur at most once in the clean output.

**Validates: Requirements 4.3, 7.3**

---

##### Property 14: Review Report Schema Consistency

*For any* flagged row, including rows with fewer or more values than the original header, the review report SHALL contain the original columns followed by exactly four fields: `Original Row Number`, `Flag Reason`, `Excel Row Number`, and `Duplicate of Excel Row`. The test SHALL verify the original row number, reason, Excel row number (`Original Row Number + 1`), and an empty duplicate-reference field for the non-duplicate example.

**Validates: Requirements 8.2, 8.3, 8.4, 8.5, 8.7**

---


### 11.3 Test Evidence

The latest verified full test run on 2026-11-26 produced:

```text
122 passed in 4.08s
```

The tests were run using the project's virtual environment.

The tested environment included Python 3.14.8 and the project dependencies.

This result is evidence of the test run at that time. It is not a guarantee that every future code change will pass.

### 11.4 End-to-End Testing

Unit and property-based tests provide coverage of individual processing components.

The automated sample integration test in `tests/test_sample_csv_integration.py` loads the bundled sample CSV, reads and validates its records, generates clean and review CSV exports, and checks record counts, row integrity, report columns, Excel row numbers, and duplicate references. This verifies the sample-data processing and export integration. It does not launch Streamlit or automate browser interactions.

### 11.5 Coverage

A 90% code-coverage target may be used as a quality objective.

It should not be described as achieved unless a coverage measurement confirms it.

## 12. Dependencies and Runtime

The project uses the dependency versions pinned in `requirements.txt`.

The documented pins include:

- Streamlit 1.46.0
- pytest 8.3.5
- Hypothesis 6.165.0

The application has been tested in the project's Windows virtual environment with Python 3.14.8.

Compatibility with other Python versions and operating systems should be verified separately rather than assumed.

## 13. Deployment

The application has a Streamlit-hosted deployment:

https://myai-dataflow-duaji4rohjsc7pwxx9y6fx.streamlit.app/

The deployment uses the project dependencies and bundled sample data.

The sample-data path is resolved relative to the application file.

The live application and sample-data workflow have previously been checked.

A manual local Windows UI smoke test has been performed. It covered the CSV sample workflow and downloads, JSON validation, and malformed JSON handling. This was a manual check, not an automated browser test. Future deployment changes should be verified independently.

## 14. Data Integrity and Design Principles

The application should follow these principles:

1. Preserve original row values in review records.
2. Identify the source row for every flagged record.
3. Keep the first occurrence of an exact duplicate as the reference.
4. Make validation reasons understandable.
5. Keep clean and flagged records distinguishable.
6. Use decimal arithmetic for financial calculations.
7. Avoid silently discarding invalid or duplicate records.
8. Keep processing logic separated from presentation logic.
9. Preserve the original source file.
10. Make exported reports traceable to source records.

## 15. Current Scope and Limitations

The following distinctions are important when describing the current application:

| Capability | Current status |
|---|---|
| CSV upload and reading | Implemented |
| Missing-value detection | Implemented |
| Exact duplicate detection | Implemented |
| Invoice amount validation | Implemented |
| Clean CSV export | Implemented |
| Review report with four extra columns | Implemented |
| Supplier-wise reconciliation | Implemented |
| JSON sales validation | Implemented |
| JSON validation CSV report | Implemented |
| Standalone currency validator | Implemented as a separate module |
| Currency validator integrated into dashboard | Not currently integrated |
| General-purpose JSON Schema validation | Not implemented |
| Automated sample CSV validation and export integration | Verified by `tests/test_sample_csv_integration.py` |
| 90% test coverage | Target, not verified |
| Local Windows Streamlit UI smoke test | Manually verified; not automated |

## 16. Future Improvements

Potential future improvements include:

- Automated browser-level end-to-end testing of the Streamlit interface.
- Measured code coverage and improved coverage where necessary.
- Integration of currency validation into the user interface, if approved.
- Broader JSON validation options.
- Additional supplier reconciliation checks.
- Improved user guidance for correcting flagged records.
- More comprehensive deployment and compatibility testing.

Future improvements should be implemented through the project's requirements and task workflow, with tests added before considering them complete.

---

**End of Design Document**
