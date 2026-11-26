# MyAI DataFlow — Product Overview



## Product Purpose



MyAI DataFlow is a Python-based, browser-accessible data validation and review application designed initially for wholesalers and businesses working with supplier sales and invoice data.



Its purpose is to help users identify data-quality problems, validate invoice calculations, review questionable records, and produce reliable reports without silently changing or discarding their original source data.



## Target Users



* Wholesalers handling supplier sales and purchase records
* Small and medium-sized businesses processing CSV data
* Business operators who need practical data validation and reconciliation
* Users who need clear reports to review incorrect or incomplete records



## Current Features



### 1\. CSV Validation

* Upload CSV files or use the bundled sample dataset.
* Check required invoice columns.
* Identify missing values and incomplete rows.
* Detect exact duplicate records.
* Preserve the first occurrence and identify subsequent duplicates.



### 2\. Invoice Validation

* Validate quantity, unit price, and reported total.
* Use decimal arithmetic for financial calculations.
* Identify invalid or inconsistent invoice amounts.



### 3\. Review and Export

* Separate clean records from flagged records.
* Explain why each record was flagged.
* Preserve original row references and Excel row numbers.
* Identify the original occurrence of duplicate records.
* Download clean CSV files and review reports.



### 4\. Supplier Reconciliation

* Summarize invoice amounts by supplier.
* Exclude duplicate records from reconciliation totals.
* Retain invalid invoice amounts for visibility rather than silently removing them.



### 5\. JSON Sales Validation

* Accept JSON sales data through the application's JSON workflow.
* Validate the supported sales field and report record status.
* Export validation results for review.



## Data Integrity Principles



1\. Never silently modify the original uploaded data.

2\. Never silently discard flagged records.

3\. Preserve row references so users can trace reported issues.

4\. Explain validation failures clearly.

5\. Keep clean records and flagged records distinguishable.

6\. Use accurate financial calculations.

7\. Make reports consistent with the underlying validation results.

8\. Treat flagged records as requiring review, not automatically corrected data.



## Product Scope and Limitations



* The current application is built around CSV invoice validation, reconciliation, and a limited JSON sales-validation workflow.
* The JSON validator is not a general-purpose JSON schema engine.
* The currency validator exists as a standalone module and is not currently integrated into the application workflow.
* The current CSV upload limit is 50 MB.
* The application does not automatically guarantee that flagged business records are correct after review; users remain responsible for reviewing them.



## Product Direction



The longer-term direction is to develop MyAI DataFlow into a practical data-quality and automation platform for wholesalers.



Potential future capabilities may include:

* Additional supplier data formats.
* More comprehensive financial validation.
* Automated supplier reconciliation workflows.
* Business reporting and analytics.
* Integrations with accounting and business systems.



Future capabilities must be treated as planned work until implemented, tested, and verified.



## Development Principle



Prioritize correctness, traceability, maintainability, and practical business value over adding features quickly.
