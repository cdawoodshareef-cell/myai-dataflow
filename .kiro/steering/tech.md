# MyAI DataFlow — Technical Standards



## 1. Technology Stack



The project uses the following technologies:



- \*\*Programming language:\*\* Python

- \*\*Python environment:\*\* Python 3.14.8 on Windows (verified development environment)

- \*\*Web application framework:\*\* Streamlit

- \*\*Testing framework:\*\* pytest

- \*\*Property-based testing:\*\* Hypothesis

- \*\*Data formats:\*\* CSV, JSON

- \*\*Financial calculations:\*\* Python Decimal

- \*\*Version control:\*\* Git

- \*\*Deployment platform:\*\* Streamlit Community Cloud



Do not assume that other Python versions or operating systems have been tested unless verification evidence exists.



## 2. Python Environment



The project uses a local virtual environment:



```text

.venv\\

```



Use the project's virtual environment rather than assuming packages are installed in system Python.



Preferred commands from the project root:



```cmd

.venv\\Scripts\\python.exe --version

.venv\\Scripts\\python.exe -m pytest tests/ -v

```



Use `py` for system-level Python checks only when appropriate.



Do not switch Python installations, recreate the virtual environment, or upgrade dependencies without a clear reason and user approval.



## 3. Dependency Management



The `requirements.txt` file defines project dependencies.



Previously verified dependency pins include:



- Streamlit 1.46.0

- pytest 8.3.5

- Hypothesis 6.165.0



Before adding a dependency:



1\. Check whether the existing Python standard library or installed packages already provide the required functionality.

2\. Explain why the dependency is needed.

3\. Avoid unnecessary package additions.

4\. Update dependency documentation consistently.

5\. Verify installation and relevant tests.



Do not upgrade or replace dependency versions without checking compatibility.



## 4. Application Architecture



The application is divided into focused modules:



- `app.py` — Streamlit user interface and application workflows.

- `csv\_reader.py` — CSV input parsing and validation of file structure.

- `validator.py` — required-column checks, missing values, duplicate detection, and row validation.

- `invoice\_validator.py` — invoice amount and calculation validation.

- `currency\_validator.py` — standalone currency validation module; not currently integrated into the application workflow.

- `json\_validator.py` — supported JSON sales validation.

- `reconciliation\_report.py` — supplier-wise reconciliation.

- `exporter.py` — clean CSV, review report, and reconciliation exports.



Preserve separation of responsibilities. Do not move substantial application logic into `app.py` when an appropriate module already exists.



Inspect the current source code before changing module interfaces or responsibilities.



## 5. Financial Calculation Standards



Financial calculations must prioritize accuracy.



- Use `decimal.Decimal` for monetary arithmetic.

- Avoid binary floating-point arithmetic for financial calculations.

- Use the established rounding policy, including `ROUND_HALF_UP` where applicable.

- Validate missing, nonnumeric, non-finite, and invalid values.

- Do not silently convert invalid financial values into zero.

- Preserve sufficient precision during intermediate calculations.

- Keep validation results consistent with exported reports and reconciliation totals.



Do not change financial calculation or rounding rules without reviewing existing tests and explaining the impact.



## 6. Data Integrity Standards



The application must preserve source-data traceability.



- Never overwrite the original uploaded file.

- Do not silently delete invalid or duplicate records.

- Preserve original row numbers.

- Preserve duplicate references to the first occurrence.

- Keep clean and flagged records separate.

- Include meaningful validation reasons.

- Ensure Excel row references account for the header row.

- Ensure exported data accurately reflects validation results.



Reconciliation must continue to exclude duplicate records while retaining invalid invoice amounts for visibility, unless an explicitly approved requirement changes this behavior.



## 7. Testing Standards



Use pytest for unit and integration tests and Hypothesis for property-based testing.



Test coverage should include:



- Valid input.

- Missing and incomplete values.

- Invalid data types and formats.

- Duplicate records.

- Financial calculation boundaries.

- Empty and malformed files.

- Export accuracy.

- Row-number traceability.

- Supplier reconciliation.

- JSON validation.

- Error handling.



When changing code:



1\. Identify the affected modules.

2\. Inspect relevant existing tests.

3\. Add or update tests for changed behavior.

4\. Run focused tests first.

5\. Run the full test suite when appropriate.

6\. Report actual test results.



The latest verified full-suite result on 2026-11-26 was 121 passed in 5.81 seconds using Python 3.14.8. Treat this as recorded evidence; rerun the suite before relying on it after code changes.



A target of at least 90% test coverage is a goal, not a verified result until coverage is measured.



## 8. Code Quality



- Prefer readable, maintainable Python.

- Use descriptive function and variable names.

- Keep functions focused on one responsibility.

- Handle expected exceptions explicitly.

- Avoid unnecessary abstractions.

- Avoid duplicate business logic.

- Preserve existing public interfaces unless a change is necessary and approved.

- Add comments for non-obvious business rules.

- Follow the existing project style.



## 9. Windows Development Rules



The primary development environment is Windows.



- Use Windows-compatible paths and commands.

- Preserve the existing `.venv`.

- Do not assume PowerShell and CMD have identical command syntax.

- Use explicit virtual-environment Python commands for testing.

- Avoid destructive commands.

- Do not delete project files or backups without explicit approval.



When giving instructions to the developer, provide one small command at a time, explain its purpose, and wait for the actual terminal output before proceeding.



## 10. Safe Change Management



Before modifying an existing important file:



1\. Inspect the current file.

2\. Understand its dependencies and existing behavior.

3\. Create a backup when the change is significant.

4\. Make the smallest necessary change.

5\. Inspect the resulting file.

6\. Run relevant tests.

7\. Report what changed and what remains unverified.



Never replace a complete source file merely to make a small correction unless there is a clear reason.



Do not overwrite user-created backups.



Do not stage, commit, push, or publish changes without explicit user approval.



## 11. Evidence-Based Development



Distinguish clearly between:



- Implemented functionality.

- Functionality covered by passing tests.

- Manually verified functionality.

- Planned functionality.

- Unverified assumptions.



Never claim a feature works merely because it appears in requirements or design documentation.



Inspect source code and test evidence before reporting implementation status.



Do not mark outstanding tasks as completed without evidence.



## 12. Deployment Standards



The application is deployed through Streamlit Community Cloud.



Before deployment-related changes:



- Check `requirements.txt`.

- Verify required application files are included.

- Verify bundled sample data is available.

- Check relative file paths.

- Test the affected workflows locally where possible.

- Avoid exposing credentials, secrets, or private business data.



Do not claim a deployment is successful until the deployed application has been checked.



## 13. Change Priority



Prioritize changes in this order:



1\. Data correctness and integrity.

2\. Financial calculation accuracy.

3\. Traceability and auditability.

4\. Automated test reliability.

5\. Application stability.

6\. Maintainability.

7\. User experience.

8\. Additional features.



Avoid adding complexity without a clear business or technical benefit.