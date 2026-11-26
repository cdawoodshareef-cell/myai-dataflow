# MyAI DataFlow — CSV Error Detective

**A practical data-quality and reconciliation application for wholesalers and small businesses.**

MyAI DataFlow helps businesses inspect supplier and invoice data, identify data-quality problems, review questionable records, and generate structured reports.

The application focuses on traceability and data integrity: it identifies problems without silently changing or discarding the original source records.

## Live Application

[Open MyAI DataFlow](https://myai-dataflow-duaji4rohjsc7pwxx9y6fx.streamlit.app/)

## The Problem

Businesses working with supplier sales and invoice data can encounter missing information, duplicate records, inconsistent invoice amounts, and unreliable reconciliation totals.

Finding these problems manually takes time and makes it difficult to trace why a record was flagged.

MyAI DataFlow provides a structured workflow to validate records, explain issues, separate clean and flagged data, and produce reviewable reports.

## Features

### CSV validation
- Upload CSV files or use the sample dataset.
- Check required fields and identify missing values.
- Detect exact duplicate records.
- Preserve the first occurrence and flag subsequent duplicates.

### Invoice validation
- Validate invoice quantities, unit prices, and reported totals.
- Use decimal arithmetic for financial calculations.
- Identify invalid or inconsistent invoice amounts.

### Review reports and exports
- Separate clean records from flagged records.
- Explain why each record was flagged.
- Preserve original row references and Excel row numbers.
- Identify matching duplicate records.
- Export clean CSV files and review reports.

### Supplier reconciliation
- Generate supplier-wise financial summaries.
- Exclude duplicate records from reconciliation totals.
- Retain invalid invoice amounts for visibility and review.

### JSON sales validation
- Validate supported JSON sales records.
- Handle malformed JSON input.
- Report validation results for review.

## How It Works

1. Upload a supplier or invoice CSV file, or use the sample dataset.
2. Run the available validation checks.
3. Inspect clean records and flagged records.
4. Review the reasons for each flagged record and trace its original row.
5. Download the resulting clean data and review reports.
6. Use supplier reconciliation and JSON validation workflows where applicable.

## Technology

- Python
- Streamlit
- pytest
- Hypothesis
- CSV and JSON processing
- Decimal-based financial calculations

## Testing and Verification

**Latest recorded full test run: November 26, 2026**

- Python version: 3.14.8
- Result: **122 tests passed**

The test suite includes unit tests, integration tests, and Hypothesis property-based tests.

Property-based testing checks defined correctness properties across generated inputs, complementing individual example-based tests.

## Kiro Development Workflow

Kiro was used to structure and guide development through specification-driven work and project-specific steering documents.

The repository includes:

- `.kiro/specs/csv-error-detective/requirements.md` — feature requirements.
- `.kiro/specs/csv-error-detective/design.md` — technical design and documented correctness properties.
- `.kiro/specs/csv-error-detective/tasks.md` — implementation tasks and progress.
- `.kiro/specs/csv-error-detective/tasks.meta.json` — task metadata.
- `.kiro/steering/product.md` — product purpose, users, features, scope, and principles.
- `.kiro/steering/structure.md` — project structure guidance.
- `.kiro/steering/tech.md` — technical conventions and guidance.

The workflow used requirements and design documents to guide implementation, followed by testing and documentation of the resulting behavior.

Hypothesis property-based tests were used to check correctness properties that go beyond a small set of manually selected examples.

## Project Structure

```text
myai-dataflow/
├── .kiro/
│   ├── specs/
│   │   └── csv-error-detective/
│   │       ├── requirements.md
│   │       ├── design.md
│   │       ├── tasks.md
│   │       └── tasks.meta.json
│   └── steering/
│       ├── product.md
│       ├── structure.md
│       └── tech.md
├── .streamlit/
├── tests/
├── app.py
├── csv_reader.py
├── validator.py
├── invoice_validator.py
├── json_validator.py
├── reconciliation_report.py
├── exporter.py
├── currency_validator.py
├── sample_data.csv
├── requirements.txt
└── LICENSE
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/cdawoodshareef-cell/myai-dataflow.git
cd myai-dataflow
```

### 2. Create a virtual environment

```bash
py -m venv .venv
```

### 3. Activate the environment

Windows CMD:

```cmd
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the application

```bash
streamlit run app.py
```

## Run Tests

```bash
python -m pytest -q
```

## Scope and Limitations

- The current application focuses on CSV invoice validation, reconciliation, and a limited JSON sales-validation workflow.
- The JSON validator is not a general-purpose JSON Schema engine.
- The currency validator is a standalone module and is not currently integrated into the main application workflow.
- The current CSV upload limit is 50 MB.
- Flagged records require human review; the application does not automatically guarantee their correction.
- Streamlit interface smoke testing has been performed manually, alongside automated tests.

## Development Background

The application was developed for the Kiroween 2026 project period. Existing supplier data and business knowledge were used as project inputs; the application implementation and competition-specific development work were developed for this project.

## Data Integrity Principles

1. Never silently modify original uploaded data.
2. Never silently discard flagged records.
3. Preserve row references for traceability.
4. Explain validation failures clearly.
5. Keep clean and flagged records distinguishable.
6. Use accurate financial calculations.
7. Keep reports consistent with validation results.
8. Treat flagged records as requiring review, not automatically corrected data.

## License

This project is released under the [MIT License](LICENSE).