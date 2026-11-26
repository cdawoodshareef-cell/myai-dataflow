# MyAI DataFlow — Project Structure



## 1. Project Overview



MyAI DataFlow is a Python-based application for validating supplier and invoice data. Its primary browser interface uses Streamlit.



The project includes CSV reading, row validation, invoice validation, supplier reconciliation, and downloadable reports. Separate modules also provide JSON sales validation and currency-code validation.



The project follows a modular structure so that individual responsibilities can be maintained and tested separately.



## 2. Project Directory Layout



```text

myai_dataflow/

│

├── app.py

├── csv_reader.py

├── validator.py

├── invoice_validator.py

├── currency_validator.py

├── json_validator.py

├── reconciliation_report.py

├── exporter.py

│

├── requirements.txt

├── sample_data.csv

├── LICENSE

│

├── tests/

│   ├── test_csv_reader.py

│   ├── test_csv_reader_coverage.py

│   ├── test_currency_validator.py

│   ├── test_exporter.py

│   ├── test_invoice_edge_cases.py

│   ├── test_invoice_integration.py

│   ├── test_invoice_validator.py

│   ├── test_json_validator.py

│   ├── test_properties.py

│   ├── test_reconciliation_report.py

│   ├── test_sample_csv_integration.py

│   └── test_validator.py

│

└── .kiro/

&#x20;   ├── specs/

&#x20;   │   └── csv-error-detective/

&#x20;   │       ├── requirements.md

&#x20;   │       ├── design.md

&#x20;   │       ├── tasks.md

&#x20;   │       └── tasks.meta.json

&#x20;   │

&#x20;   └── steering/

&#x20;       ├── product.md

&#x20;       ├── tech.md

&#x20;       └── structure.md

```



Additional backup files, development environment folders, and generated test or cache files may also exist. Preserve backup files unless their removal is explicitly approved.



## 3. Application Entry Point



### `app.py`



The main Streamlit application entry point.



Responsibilities include:

- Providing the browser-based user interface.

- Accepting uploaded CSV files.

- Coordinating the CSV reading and validation workflow.

- Displaying validation results.

- Providing downloadable reports.

- Generating supplier reconciliation summaries.



The main workflow function identified in the file is:



```python

_run_validation(file_obj, source_label)

```



Direct imports identified in `app.py`:



- `csv_reader`

- `validator`

- `exporter`

- `generate_reconciliation_summary` from `reconciliation_report`



Do not assume that every standalone module is directly integrated into the Streamlit interface.



## 4. Python Module Responsibilities



### `csv_reader.py`



Main function:



```python

read_csv(file_obj)

```



Responsibilities:

- Reading CSV input.

- Returning column names and data rows.

- Handling supported binary and file-like inputs.

- Detecting invalid UTF-8 input.

- Rejecting empty files and header-only files.

- Detecting rows containing more fields than the header.



### `validator.py`



Main function:



```python

validate_rows(...)

```



Data structures:

- `FlaggedRow`

- `ValidationResult`



Responsibilities:

- Checking required columns.

- Detecting missing required values.

- Detecting duplicate rows.

- Tracking the first occurrence of duplicate records.

- Separating clean and flagged records.

- Recording review reasons.



### `invoice_validator.py`



Functions:

- `calculate_invoice_total(quantity, unit_price)`

- `validate_invoice_amount(quantity, unit_price, reported_total)`



Responsibilities:

- Calculating expected invoice totals.

- Validating reported invoice amounts.

- Handling invalid and non-finite numeric inputs.

- Applying Decimal-based financial calculations and the established rounding policy.



### `currency_validator.py`



Function:



```python

is_supported_currency(code)

```



Responsibilities:

- Checking supported currency codes.



Integration status: This is a standalone module and is not currently integrated into the main application workflow.



### `json_validator.py`



Functions:

- `validate_sales(raw_json)`

- `validate_json_records(records)`



Responsibilities:

- Validating the supported JSON sales format.

- Checking sales values and expected JSON object structure.

- Validating collections of JSON records.



This is a focused JSON sales validator, not a general-purpose JSON schema validation framework.



### `reconciliation_report.py`



Main function:



```python

generate_reconciliation_summary(column_names, data_rows)

```



Responsibilities:

- Generating supplier-level reconciliation summaries.

- Tracking invoice counts.

- Summarizing valid and invalid invoices.

- Calculating reported and calculated amounts.

- Reporting discrepancies.



Duplicate invoices are excluded from reconciliation totals, while invalid invoices remain represented in the reconciliation results.



### `exporter.py`



Functions:

- `generate_clean_csv(...)`

- `generate_review_report(...)`

- `generate_reconciliation_csv(summary)`



Responsibilities:

- Generating clean CSV downloads.

- Generating flagged-row review reports.

- Exporting supplier reconciliation summaries.



The review report includes row traceability information, including:

- Original Row Number

- Flag Reason

- Excel Row Number

- Duplicate of Excel Row



## 5. Main CSV Validation Workflow



The primary application workflow can be understood as:



1\. User uploads a CSV file through the Streamlit interface.

2\. `csv_reader.py` reads the file and returns headers and data rows.

3\. `validator.py` checks required columns, missing values, and duplicates.

4\. Invoice validation is performed where the required invoice fields are available.

5\. Clean and flagged records are prepared for display and export.

6\. Supplier reconciliation results are generated.

7\. `exporter.py` prepares downloadable outputs.



The application should preserve source-row traceability throughout validation and reporting.



## 6. Invoice Validation and Financial Integrity



Invoice calculations use Decimal-based arithmetic.



Important principles:

- Reject invalid numeric inputs.

- Reject non-finite financial values.

- Validate positive quantity and unit price where required.

- Calculate expected totals using the established rounding policy.

- Compare calculated totals with reported totals.

- Avoid silently changing original source values.



Do not modify financial calculation or rounding rules without reviewing existing tests and documenting the impact.



## 7. Supplier Reconciliation



Supplier reconciliation summarizes invoice information by supplier.



The report includes:

- Invoice count

- Valid invoice count

- Invalid invoice count

- Reported amount

- Calculated amount

- Discrepancy



Duplicate records are excluded from reconciliation totals. Invalid invoices must not silently disappear from the reconciliation results.



## 8. Test Organization



The `tests/` directory contains tests for the main application modules.



| Test file | Main responsibility |

|---|---|

| `test_csv_reader.py` | CSV reading |

| `test_csv_reader_coverage.py` | CSV reader edge cases |

| `test_currency_validator.py` | Currency validation |

| `test_exporter.py` | Export generation |

| `test_invoice_edge_cases.py` | Invoice edge cases |

| `test_invoice_integration.py` | Invoice integration |

| `test_invoice_validator.py` | Invoice calculations |

| `test_json_validator.py` | JSON sales validation |

| `test_properties.py` | Property-based validation checks |

| `test_reconciliation_report.py` | Supplier reconciliation |

| `test_sample_csv_integration.py` | End-to-end sample CSV validation and export checks |

| `test_validator.py` | Core row validation |



The latest verified full-suite run on 2026-11-26 completed with 121 tests passed in 5.81 seconds using Python 3.14.8.



This is recorded passing-test evidence, not a test-coverage measurement. Rerun the suite after code changes before relying on this result.



Run the project test suite using the local virtual environment:



```cmd

.venv\\Scripts\\python.exe -m pytest tests/ -v

```



## 9. Dependencies and Environment



The project uses the following pinned dependencies in `requirements.txt`:



- Streamlit 1.46.0

- pytest 8.3.5

- Hypothesis 6.165.0



The development environment uses Python 3.14.8 on Windows.



The local virtual environment is stored in `.venv/`.



## 10. Kiro Documentation



The `.kiro/` directory contains project specifications and steering documentation.



### Specifications



`.kiro/specs/csv-error-detective/`



Contains:

- `requirements.md` — approved project requirements.

- `design.md` — technical design.

- `tasks.md` — implementation tasks.

- `tasks.meta.json` — Kiro task metadata.



### Steering



`.kiro/steering/`



Contains:

- `product.md` — product purpose, capabilities, and principles.

- `tech.md` — technical standards and development rules.

- `structure.md` — project architecture and file responsibilities.



Keep these documents consistent with the actual implementation.



## 11. Safe Development and Change Management



- Inspect existing code before modifying it.

- Understand module dependencies before changing interfaces.

- Preserve existing working functionality.

- Create backups before significant edits.

- Make small, testable changes.

- Run relevant tests after modifications.

- Avoid deleting existing backups or project files.

- Do not stage, commit, or push changes without explicit approval.

- Update documentation when actual architecture or responsibilities change.



## 12. Architecture Maintenance Principle



The project structure document must describe the actual implementation, not planned or assumed functionality.



When a module is added, removed, integrated, or substantially changed, review this document and update it only after verifying the corresponding code and tests.