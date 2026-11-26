# Requirements Document

## Introduction

MyAI DataFlow — CSV Error Detective is a browser-based Python web application designed to help wholesalers inspect, validate, reconcile, and review supplier invoice data.

The Application provides CSV validation, invoice amount verification, duplicate detection, supplier-wise financial reconciliation, and JSON sales validation.

For CSV files, users can upload supplier invoice data or load a bundled sample file. The Application checks required values, exact duplicates, and invoice calculations. It identifies invalid records, displays validation results, and provides downloadable clean CSV, review report, and reconciliation report files.

The Review Report includes original row references, Excel row references, validation reasons, and duplicate references to help users locate and correct records in their original spreadsheets.

The Application also provides a JSON validation workflow that checks sales records for valid JSON structure and acceptable sales values.

The Application runs locally using Python and Streamlit and can also be deployed to a publicly accessible hosting environment. Its validation and reporting functionality does not require paid APIs or external validation services.

## Glossary

- **Application**: MyAI DataFlow — CSV Error Detective.
- **Web_Framework**: Streamlit, used to provide the browser-based interface.
- **Browser_Client**: The web browser through which users interact with the Application.
- **CSV_File**: A comma-separated values file uploaded for validation.
- **Supplier_Invoice_CSV**: A CSV file containing supplier invoice records.
- **Header_Row**: The first row of a CSV file containing column names.
- **Required_Column**: A column that must be present in the CSV header.
- **Missing_Value**: A required cell that is empty, contains only whitespace, or is absent from a row.
- **Exact_Duplicate**: A row whose values across all columns match a previously processed row.
- **Flagged_Row**: A record identified as having missing values, being a duplicate, or failing invoice amount validation.
- **Clean_CSV**: The downloadable CSV containing rows that pass the validation rules.
- **Review_Report**: The downloadable CSV containing flagged records and their review information.
- **Excel_Row_Number**: The original data row number plus one, accounting for the header row.
- **Duplicate_Reference**: The Excel row number of the first occurrence of a duplicate record.
- **Invoice_Amount_Validation**: The comparison of the reported invoice total against the calculated quantity multiplied by unit price.
- **Reconciliation_Report**: The supplier-wise financial summary generated from invoice records.
- **JSON_Sales_Record**: A JSON object containing a sales field that the Application validates.
- **Sample_CSV**: The synthetic supplier invoice CSV bundled with the Application.
- **Validator**: The component responsible for checking CSV records.
- **Reason**: A human-readable explanation of why a record was flagged.

---

## Requirements

### Requirement 1: CSV File Upload

**User Story:** As a wholesaler, I want to upload a supplier invoice CSV file so that the Application can validate its contents.

#### Acceptance Criteria

1. THE Application SHALL provide a file selection interface that accepts CSV files.
2. THE Application SHALL reject unsupported file formats with an appropriate error message.
3. THE Application SHALL read CSV data using UTF-8 encoding.
4. THE Application SHALL support binary file uploads and preserve original cell values.
5. IF the file cannot be decoded or read, THEN THE Application SHALL display an appropriate error message.
6. IF the CSV contains no header or no data rows, THEN THE Application SHALL display an appropriate error message and halt processing.
7. THE Application SHALL support a maximum uploaded file size of 50 MB.
8. THE Application SHALL allow the user to select another file after an upload or validation error.

### Requirement 2: Required Column Definition

**User Story:** As a wholesaler, I want the Application to recognize the required invoice columns so that incomplete records can be identified.

#### Acceptance Criteria

1. THE Application SHALL recognize the following required columns:

   - `Invoice Number`
   - `Invoice Date`
   - `Supplier Name`
   - `Product Code`
   - `Product Description`
   - `Quantity`
   - `Unit Price`
   - `Total Amount`

2. THE Application SHALL identify required columns without depending on capitalization differences or surrounding whitespace in header names.
3. IF one or more required columns are absent, THEN THE Application SHALL report the missing column names and halt CSV validation.
4. THE Application SHALL treat empty, whitespace-only, and absent cell values as Missing_Values.
5. THE Application SHALL support rows containing fewer fields than the header without causing an index error.

### Requirement 3: Missing Value Detection

**User Story:** As a wholesaler, I want to identify incomplete invoice records so that I can correct them.

#### Acceptance Criteria

1. THE Validator SHALL inspect every Required_Column for Missing_Values.
2. WHEN a record contains missing required values, THE Validator SHALL flag that record.
3. THE Reason SHALL identify all affected column names.
4. WHEN multiple required values are missing, THE Application SHALL report all affected columns in one reason.
5. THE Validator SHALL record the original 1-based data row number, excluding the header row.

### Requirement 4: Exact Duplicate Detection

**User Story:** As a wholesaler, I want to identify duplicate invoice records so that redundant records can be reviewed.

#### Acceptance Criteria

1. THE Validator SHALL compare each row across all columns against previously processed rows.
2. THE Validator SHALL identify the first occurrence of an exact duplicate.
3. THE Validator SHALL flag subsequent identical records.
4. THE duplicate reason SHALL reference the actual 1-based data row number of the first occurrence.
5. WHEN the first occurrence is valid, THE Application SHALL retain it in the clean output.
6. WHEN the first occurrence has missing values, THE Application SHALL flag it for its missing values.
7. WHEN a subsequent duplicate also contains missing values, THE Application SHALL include both duplicate and missing-value reasons.
8. THE Application SHALL retain the first-occurrence reference when three or more identical records exist.
9. THE Application SHALL exclude duplicate records from the Clean_CSV.
10. THE Application SHALL identify duplicate records separately for financial reconciliation.

### Requirement 5: Invoice Amount Validation

**User Story:** As a wholesaler, I want the Application to verify invoice calculations so that incorrect invoice totals can be identified.

#### Acceptance Criteria

1. THE Application SHALL calculate the expected invoice total using:

   `Quantity × Unit Price`

2. THE Application SHALL use decimal arithmetic for invoice calculations.
3. THE Application SHALL round calculated totals to two decimal places using half-up rounding.
4. THE Application SHALL flag an invoice when its reported total does not match the calculated total.
5. THE Application SHALL reject non-numeric, non-finite, zero, or negative quantities and unit prices.
6. THE Application SHALL reject missing or invalid invoice amount inputs.
7. THE Application SHALL identify invalid invoice amounts using an appropriate validation reason.
8. THE Application SHALL combine invoice validation reasons with other applicable reasons for the same record.
9. THE Application SHALL preserve original invoice values in the review report.

### Requirement 6: Flagged Row Reporting

**User Story:** As a wholesaler, I want a clear summary of invalid records so that I can understand what requires correction.

#### Acceptance Criteria

1. THE Application SHALL display the total number of processed records.
2. THE Application SHALL display the number of clean records.
3. THE Application SHALL display the number of flagged records.
4. THE Application SHALL display flagged records with their original values and validation reasons.
5. THE Application SHALL present flagged records in ascending original row order.
6. THE Application SHALL support multiple validation reasons for a single record.
7. THE Application SHALL maintain the count invariant:

   `Clean Count + Flagged Count = Total Count`

### Requirement 7: Clean CSV Export

**User Story:** As a wholesaler, I want to download validated invoice records without flagged entries.

#### Acceptance Criteria

1. THE Application SHALL provide a downloadable Clean_CSV after validation.
2. THE Clean_CSV SHALL retain the original header and column order.
3. THE Clean_CSV SHALL contain only records that passed all applicable validation checks.
4. THE Clean_CSV SHALL preserve original cell values without modification.
5. THE Clean_CSV SHALL be UTF-8 encoded.
6. IF all records are flagged, THEN THE Application SHALL produce a header-only Clean_CSV.
7. THE Application SHALL provide a notice when no clean records are available.

### Requirement 8: Review Report Export

**User Story:** As a wholesaler, I want a detailed review report so that I can locate and correct invalid records in my original spreadsheet.

#### Acceptance Criteria

1. THE Application SHALL provide a downloadable Review_Report.
2. THE Review_Report SHALL retain all original CSV columns.
3. THE Review_Report SHALL append these four columns:

   - `Original Row Number`
   - `Flag Reason`
   - `Excel Row Number`
   - `Duplicate of Excel Row`

4. THE Original Row Number SHALL represent the 1-based data row number, excluding the header.
5. THE Excel Row Number SHALL equal the Original Row Number plus one.
6. THE Duplicate of Excel Row SHALL identify the Excel row number of the first occurrence when a record is a duplicate.
7. THE duplicate reference SHALL remain empty for records that are not duplicates.
8. THE Review_Report SHALL contain one record per flagged row.
9. THE Review_Report SHALL preserve original record values.
10. THE Review_Report SHALL list flagged records in ascending row order.
11. THE Review_Report SHALL be UTF-8 encoded.
12. IF no records are flagged, THEN THE Application SHALL produce a header-only report and display an appropriate notice.

### Requirement 9: Supplier-Wise Financial Reconciliation

**User Story:** As a wholesaler, I want financial totals summarized by supplier so that I can review invoice amounts and identify discrepancies.

#### Acceptance Criteria

1. THE Application SHALL generate a supplier-wise reconciliation summary from the uploaded invoice data.
2. THE Application SHALL calculate reported and calculated invoice amounts.
3. THE Application SHALL identify discrepancies between reported and calculated amounts.
4. THE Application SHALL display relevant invoice counts and financial totals.
5. THE Application SHALL identify invalid invoice records in the reconciliation results.
6. THE Application SHALL exclude duplicate records from financial totals to avoid double counting.
7. THE Application SHALL retain invalid invoice records in the reconciliation results rather than silently removing them.
8. THE Application SHALL display supplier-wise reconciliation results in the dashboard.
9. THE Application SHALL provide a downloadable reconciliation CSV.
10. THE reconciliation CSV SHALL include a total summary and information about excluded duplicate records.
11. THE Application SHALL handle cases where reconciliation cannot be performed because required data or headers are unavailable.

### Requirement 10: JSON Sales Validation

**User Story:** As a wholesaler, I want to validate JSON sales records so that incorrect sales data can be identified.

#### Acceptance Criteria

1. THE Application SHALL provide a separate JSON file upload interface.
2. THE Application SHALL accept JSON objects and arrays of JSON records.
3. THE Application SHALL require each sales record to contain a `sales` field.
4. THE `sales` field SHALL contain a numeric value.
5. THE Application SHALL accept zero and non-negative sales values.
6. THE Application SHALL reject negative sales values.
7. THE Application SHALL reject strings, null values, Boolean values, and other non-numeric sales values.
8. THE Application SHALL report malformed JSON and unsupported top-level structures.
9. THE Application SHALL display a validation result for each record, including its row number and status.
10. THE Application SHALL display valid and invalid record counts.
11. THE Application SHALL provide a downloadable CSV validation report containing record numbers and validation statuses.
12. THE Application SHALL reject non-finite numeric sales values, including NaN, Infinity, and negative Infinity.
13. THE JSON workflow SHALL remain separate from the supplier invoice CSV workflow.

### Requirement 11: Sample CSV

**User Story:** As a wholesaler, I want a bundled sample file so that I can explore the Application without uploading real business data.

#### Acceptance Criteria

1. THE Application SHALL include `sample_data.csv` in the project distribution.
2. THE Sample_CSV SHALL use the eight required invoice columns.
3. THE Sample_CSV SHALL contain at least 15 data rows.
4. THE Sample_CSV SHALL contain at least three rows with missing values across different required columns.
5. THE Sample_CSV SHALL contain at least two exact duplicate records.
6. THE Sample_CSV SHALL contain at least eight fully valid, non-duplicate records.
7. THE Application SHALL provide an option to load the bundled sample into the normal validation workflow.
8. THE Application SHALL locate the sample file relative to the application script rather than relying on the current working directory.

### Requirement 12: Deployment Compatibility

**User Story:** As a wholesaler and application demonstrator, I want the Application to run locally and through a public hosting environment.

#### Acceptance Criteria

1. THE Application SHALL run on a supported Windows environment without requiring administrator privileges.
2. THE Application SHALL provide a local browser interface using Streamlit.
3. THE Application SHALL use port 8501 by default when started locally.
4. THE Application SHALL perform validation and report generation on the application server.
5. THE Application SHALL NOT require paid APIs or external validation services.
6. THE Application SHALL include a `requirements.txt` file with pinned third-party dependencies.
7. THE Application SHALL include the bundled sample CSV in the repository.
8. THE Application SHALL use paths that work independently of the terminal's current working directory.
9. WHERE deployed to a supported public hosting environment, THE Application SHALL provide its documented functionality without source-code changes.
10. THE Application SHALL provide appropriate error handling for missing files, malformed uploads, and unsupported input data.

---

## Implementation Scope Notes

The following distinctions are important when maintaining this specification:

- The currency validation module exists separately but is not currently integrated into the main application workflow.
- JSON validation currently validates the presence and value of the `sales` field; it is not a general-purpose JSON schema validator.
- The Application currently uses a 50 MB upload limit.
- The review report currently contains four additional columns.
- The current application has separate CSV validation, reconciliation, and JSON validation workflows.
- Requirements describe implemented application behavior; future enhancements must be documented separately rather than represented as completed functionality.