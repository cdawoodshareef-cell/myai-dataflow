# Requirements Document

## Introduction

MyAI DataFlow — CSV Error Detective is a browser-based Python web application for wholesalers that validates supplier sales CSV files. A user uploads a CSV file through a web browser, and the application inspects each row for missing required values and exact duplicate rows. Every flagged row is reported with its original row number and the reason it was flagged. The user can then download two output files: a clean CSV containing only the rows that passed all checks, and a review report CSV containing the flagged rows with their reasons. A synthetic sample CSV is bundled with the application for demonstration purposes. The application runs as a local web server on Windows (accessible via `localhost`) and can also be hosted at a public URL for demonstration events such as the Kiroween demo. It requires no paid APIs or external services for any of its functionality.

## Glossary

- **Application**: The CSV Error Detective browser-based Python web application being described in this document.
- **Web_Framework**: The open-source Python web framework (such as Streamlit, Gradio, or Flask) used to serve the Application's user interface in a web browser.
- **Browser_Client**: The web browser through which the user interacts with the Application.
- **CSV_File**: A comma-separated values file uploaded by the user for validation.
- **Supplier_Sales_CSV**: The specific CSV file format used by wholesalers to record supplier sales data, containing defined required columns.
- **Row**: A single data record (line) within a CSV file, identified by its 1-based row number (excluding the header row).
- **Header_Row**: The first line of a CSV file that defines column names.
- **Required_Column**: A column whose value must be present and non-empty for a row to be considered valid.
- **Missing_Value**: A cell in a Required_Column that is empty, whitespace-only, or absent.
- **Exact_Duplicate**: A row whose values in every column are identical to at least one other row already seen in the same file.
- **Flagged_Row**: A row that has been identified as having a Missing_Value or being an Exact_Duplicate.
- **Clean_CSV**: The output CSV file containing only rows that passed all validation checks.
- **Review_Report**: The output CSV file containing all Flagged_Rows, including their original row numbers and flag reasons.
- **Validator**: The component of the Application responsible for checking rows against all validation rules.
- **Sample_CSV**: A synthetic CSV file bundled with the Application that demonstrates the expected file format and contains examples of valid and invalid rows.
- **Reason**: A human-readable string describing why a row was flagged (e.g., "Missing value in column 'Invoice Number'", "Exact duplicate of row 3").

---

## Requirements

### Requirement 1: CSV File Upload

**User Story:** As a wholesaler, I want to upload a supplier sales CSV file, so that the Application can validate its contents.

#### Acceptance Criteria

1. THE Application SHALL provide a file selection interface that accepts files with a `.csv` extension.
2. WHEN a user selects a file with an extension other than `.csv`, THE Application SHALL display an error message stating that only CSV files are accepted.
3. WHEN a valid `.csv` file is selected, THE Application SHALL read the file using UTF-8 encoding.
4. IF the selected CSV_File cannot be read due to a file system error, THEN THE Application SHALL display a descriptive error message and allow the user to select a different file.
5. WHEN the CSV_File is read successfully, THE Application SHALL detect the Header_Row from the first line of the file.
6. IF the CSV_File contains no Header_Row or no data rows, THEN THE Application SHALL display an error message stating that the file is empty or malformed and halt processing.

---

### Requirement 2: Required Column Definition

**User Story:** As a wholesaler, I want the Application to know which columns are required, so that it can correctly identify missing values in supplier sales data.

#### Acceptance Criteria

1. THE Application SHALL treat the following columns as Required_Columns for a Supplier_Sales_CSV: `Invoice Number`, `Invoice Date`, `Supplier Name`, `Product Code`, `Product Description`, `Quantity`, `Unit Price`, `Total Amount`.
2. WHEN the uploaded CSV_File does not contain one or more Required_Columns in its Header_Row, THE Application SHALL display an error message listing the missing column names and halt processing.
3. THE Application SHALL treat a cell value as a Missing_Value when the cell is empty, contains only whitespace characters, or is absent from the row.

---

### Requirement 3: Missing Value Detection

**User Story:** As a wholesaler, I want to know which rows have missing required values, so that I can correct incomplete data before processing it.

#### Acceptance Criteria

1. WHEN the Validator processes a row, THE Validator SHALL check every Required_Column for a Missing_Value.
2. WHEN a row contains one or more Missing_Values, THE Validator SHALL flag the row with a Reason that identifies each affected column name.
3. WHEN a row contains Missing_Values in multiple Required_Columns, THE Validator SHALL report all affected column names in a single Reason string for that row.
4. THE Validator SHALL record the original 1-based row number of every Flagged_Row, where row numbering starts at 1 for the first data row after the Header_Row.

---

### Requirement 4: Exact Duplicate Detection

**User Story:** As a wholesaler, I want to identify exact duplicate rows, so that I can remove redundant entries before importing data into my system.

#### Acceptance Criteria

1. WHEN the Validator processes a row, THE Validator SHALL compare the row's values across all columns against all previously processed rows in the same CSV_File.
2. WHEN a row is identical in all column values to a previously processed row and the current row is not the first occurrence, THE Validator SHALL flag the current row as an Exact_Duplicate.
3. WHEN flagging a row as an Exact_Duplicate, THE Validator SHALL include in the Reason the 1-based row number of the first occurrence of the duplicate, where row numbering starts at 1 for the first data row after the Header_Row (the Header_Row itself is not counted).
4. WHEN the first occurrence of a set of identical rows contains no Missing_Values, THE Validator SHALL retain that first occurrence in the Clean_CSV and flag only subsequent occurrences as Exact_Duplicates.
5. WHEN the first occurrence of a set of identical rows contains one or more Missing_Values, THE Validator SHALL flag that first occurrence for its Missing_Values only and SHALL NOT flag it as an Exact_Duplicate.
6. WHEN a subsequent duplicate row also contains one or more Missing_Values, THE Validator SHALL flag that row with both the Exact_Duplicate reason and the Missing_Value reason in a single combined Reason string.
7. THE Validator SHALL never include a row flagged as an Exact_Duplicate in the Clean_CSV, regardless of whether the row also has Missing_Values.

---

### Requirement 5: Flagged Row Reporting

**User Story:** As a wholesaler, I want to see a clear summary of all flagged rows with reasons, so that I understand what data needs to be corrected.

#### Acceptance Criteria

1. WHEN validation is complete, THE Application SHALL display the total count of rows processed, the count of Flagged_Rows, and the count of clean rows.
2. THE Application SHALL present each Flagged_Row in a results view showing the original row number, the full row values, and the Reason for flagging.
3. WHEN a row is flagged for both a Missing_Value and being an Exact_Duplicate, THE Application SHALL report both reasons for that row.
4. WHILE displaying results, THE Application SHALL list Flagged_Rows in ascending order of their original row numbers.

---

### Requirement 6: Clean CSV Export

**User Story:** As a wholesaler, I want to download a clean CSV file, so that I can use the validated data directly in my system without manual filtering.

#### Acceptance Criteria

1. WHEN validation is complete, THE Application SHALL make a Clean_CSV available for download.
2. THE Clean_CSV SHALL contain the Header_Row from the original CSV_File as its first line.
3. THE Clean_CSV SHALL contain only the rows from the original CSV_File that were not flagged by the Validator.
4. THE Clean_CSV SHALL preserve the original column order and cell values of all included rows without modification.
5. WHEN the user initiates the Clean_CSV download, THE Application SHALL deliver the file to the Browser_Client as a downloadable file using the browser's native download mechanism.
6. IF all rows in the uploaded CSV_File are flagged, THEN THE Application SHALL write a Clean_CSV that contains only the Header_Row and display a notice that no clean rows were found.

---

### Requirement 7: Review Report Export

**User Story:** As a wholesaler, I want to download a review report of all flagged rows, so that I have a structured file I can share with my team for correction.

#### Acceptance Criteria

1. WHEN validation is complete, THE Application SHALL make a Review_Report available for download.
2. THE Review_Report SHALL be a CSV file containing the Header_Row from the original CSV_File plus two additional columns: `Original Row Number` and `Flag Reason`.
3. THE Review_Report SHALL contain one row per Flagged_Row, populated with the original cell values, the original row number in the `Original Row Number` column (using 1-based numbering where the first data row is row 1, excluding the Header_Row), and the Reason.
4. THE Review_Report SHALL list rows in ascending order of original row numbers.
5. WHEN the user initiates the Review_Report download, THE Application SHALL deliver the file to the Browser_Client as a downloadable file using the browser's native download mechanism.
6. IF no rows are flagged, THEN THE Application SHALL write a Review_Report containing only the header line and display a notice that no flagged rows were found.

---

### Requirement 8: Sample CSV

**User Story:** As a wholesaler, I want a sample CSV file bundled with the Application, so that I can explore the Application's features without needing a real data file.

#### Acceptance Criteria

1. THE Application SHALL include a Sample_CSV file in its distribution that conforms to the Supplier_Sales_CSV column structure defined in Requirement 2.
2. THE Sample_CSV SHALL contain at least 15 data rows.
3. THE Sample_CSV SHALL include at least 3 rows with one or more Missing_Values across different Required_Columns.
4. THE Sample_CSV SHALL include at least 2 rows that are Exact_Duplicates of earlier rows in the file.
5. THE Sample_CSV SHALL include at least 8 rows that are fully valid and will appear in the Clean_CSV output.
6. WHEN the user selects the option to load the Sample_CSV, THE Application SHALL load it into the validation workflow as if the user had uploaded it manually.

---

### Requirement 9: Deployment Compatibility

**User Story:** As a wholesaler running Windows, and as a demo presenter at the Kiroween event, I want the Application to run locally on Windows and optionally be accessible at a public URL, without paid APIs or cloud services, so that I can use it in my local environment and demonstrate it remotely at no additional cost.

#### Acceptance Criteria

1. THE Application SHALL run on Windows 10 and Windows 11 without requiring administrator privileges.
2. WHEN started on a local Windows machine, THE Application SHALL start a local web server and serve the user interface at `http://localhost` on a configurable port number, defaulting to port 8501.
3. THE Application SHALL perform all validation and file generation on the server side and SHALL NOT require any network connection or external API calls to complete validation or produce output files.
4. THE Application SHALL rely only on Python standard library modules and freely available open-source third-party packages installable via `pip`.
5. THE Application SHALL include a `requirements.txt` file listing all third-party dependencies with pinned version numbers.
6. WHERE the Application is deployed to a publicly accessible hosting environment, THE Application SHALL serve the same user interface and all functionality at the hosted URL without modification to the application source code.
