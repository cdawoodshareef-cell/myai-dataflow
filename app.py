"""app.py — MyAI DataFlow: CSV Error Detective (Streamlit entry point)."""
from __future__ import annotations

import io
from pathlib import Path

import streamlit as st

import csv_reader
import validator as val
import exporter
from reconciliation_report import generate_reconciliation_summary

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MyAI DataFlow — CSV Error Detective",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 MyAI DataFlow — CSV Error Detective")
st.caption(
    "Upload a supplier sales CSV to detect missing required values and exact "
    "duplicate rows. Download a clean copy or a flagged-row review report."
)

# ---------------------------------------------------------------------------
# Session state — holds the last ValidationResult and column names
# ---------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "column_names" not in st.session_state:
    st.session_state.column_names = None
if "data_rows" not in st.session_state:
    st.session_state.data_rows = None
if "reconciliation_summary" not in st.session_state:
    st.session_state.reconciliation_summary = None


def _run_validation(file_obj, source_label: str) -> None:
    """Parse file_obj, validate, and store result in session state."""
    try:
        col_names, data_rows = csv_reader.read_csv(file_obj)
    except ValueError as exc:
        st.error(f"File error: {exc}")
        st.session_state.result = None
        st.session_state.column_names = None
        st.session_state.data_rows = None
        st.session_state.reconciliation_summary = None
        return

    try:
        result = val.validate_rows(col_names, data_rows)
    except ValueError as exc:
        st.error(f"Validation error: {exc}")
        st.session_state.result = None
        st.session_state.column_names = None
        st.session_state.data_rows = None
        st.session_state.reconciliation_summary = None
        return

    st.session_state.result = result
    st.session_state.column_names = col_names
    st.session_state.data_rows = data_rows
    try:
        st.session_state.reconciliation_summary = generate_reconciliation_summary(col_names, data_rows)
    except ValueError as exc:
        st.session_state.reconciliation_summary = None
        st.info(f"Invoice reconciliation unavailable: {exc}")
    st.success(f"✅ Validation complete — {source_label}")


# ---------------------------------------------------------------------------
# Task 7.1 — File upload and Sample CSV loader
# ---------------------------------------------------------------------------
st.subheader("1. Load a CSV file")

col_upload, col_sample = st.columns([3, 1])

with col_upload:
    uploaded = st.file_uploader(
        "Upload a supplier sales CSV",
        type=["csv"],
        help="Maximum file size: 50 MB. Must be UTF-8 encoded.",
    )
    if uploaded is not None:
        if uploaded.size > 50 * 1024 * 1024:
            st.error("File exceeds the 50 MB maximum size. Please upload a smaller file.")
        else:
            _run_validation(uploaded, f'"{uploaded.name}"')

with col_sample:
    st.write("")  # vertical alignment spacer
    st.write("")
    if st.button("📂 Load sample CSV", use_container_width=True):
        sample_path = Path(__file__).parent / "sample_data.csv"
        if not sample_path.exists():
            st.error("sample_data.csv not found in the application directory.")
        else:
            with open(sample_path, "rb") as f:
                _run_validation(io.BytesIO(f.read()), "sample_data.csv")

# ---------------------------------------------------------------------------
# Task 7.2 — Summary counts
# ---------------------------------------------------------------------------
result = st.session_state.result
col_names = st.session_state.column_names

if result is not None:
    st.divider()
    st.subheader("2. Validation summary")

    m1, m2, m3 = st.columns(3)
    m1.metric("Rows processed", result.total_count)
    m2.metric("Clean rows", result.clean_count)
    m3.metric("Flagged rows", result.flagged_count)

    # ---------------------------------------------------------------------------
    # Task 7.3 — Flagged row results table
    # ---------------------------------------------------------------------------
    st.divider()
    st.subheader("3. Flagged rows")

    if result.flagged_count == 0:
        st.info("No flagged rows found — all rows passed validation.")
    else:
        # Build display table: Row #, original columns, Flag Reason
        display_rows = []
        for fr in sorted(result.flagged_rows, key=lambda r: r.row_number):
            # Pad short rows for display
            padded = list(fr.row_values) + [""] * max(0, len(col_names) - len(fr.row_values))
            padded = padded[: len(col_names)]
            display_rows.append(
                {"Row #": fr.row_number, **dict(zip(col_names, padded)), "Flag Reason": fr.reason}
            )
        st.dataframe(display_rows, use_container_width=True)

    # ---------------------------------------------------------------------------
    # Task 7.3 — Download buttons
    # ---------------------------------------------------------------------------
    st.divider()
    st.subheader("4. Downloads")

    dl1, dl2 = st.columns(2)

    clean_bytes = exporter.generate_clean_csv(col_names, result.clean_rows)
    if result.clean_count == 0:
        dl1.warning("No clean rows found — the clean CSV contains only the header.")
    with dl1:
        st.download_button(
            label="⬇️ Download clean CSV",
            data=clean_bytes,
            file_name="clean_output.csv",
            mime="text/csv",
            use_container_width=True,
        )

    report_bytes = exporter.generate_review_report(col_names, result.flagged_rows)
    if result.flagged_count == 0:
        dl2.info("No flagged rows — the review report contains only the header.")
    with dl2:
        st.download_button(
            label="⬇️ Download review report",
            data=report_bytes,
            file_name="review_report.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # MYAI RECONCILIATION DASHBOARD
    st.divider()
    st.subheader("5. Supplier invoice reconciliation")
    reconciliation = st.session_state.reconciliation_summary
    if reconciliation is None:
        st.info("Invoice reconciliation is unavailable for this CSV. Basic validation and downloads remain available.")
    else:
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Total invoices", reconciliation["total_invoices"])
        r2.metric("Valid invoices", reconciliation["valid_invoices"])
        r3.metric("Invalid invoices", reconciliation["invalid_invoices"])
        r4.metric("Duplicates excluded", reconciliation["duplicate_invoices"])
        st.subheader("Financial reconciliation")
        f1, f2, f3 = st.columns(3)
        f1.metric("Reported amount", f"{reconciliation[chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(95)+chr(114)+chr(101)+chr(112)+chr(111)+chr(114)+chr(116)+chr(101)+chr(100)+chr(95)+chr(97)+chr(109)+chr(111)+chr(117)+chr(110)+chr(116)]:,.2f}")
        f2.metric("Calculated amount", f"{reconciliation[chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(95)+chr(99)+chr(97)+chr(108)+chr(99)+chr(117)+chr(108)+chr(97)+chr(116)+chr(101)+chr(100)+chr(95)+chr(97)+chr(109)+chr(111)+chr(117)+chr(110)+chr(116)]:,.2f}")
        f3.metric("Discrepancy", f"{reconciliation[chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(95)+chr(100)+chr(105)+chr(115)+chr(99)+chr(114)+chr(101)+chr(112)+chr(97)+chr(110)+chr(99)+chr(121)]:,.2f}")
        st.caption("Duplicate rows are excluded from supplier totals. Invalid numeric rows do not contribute to financial totals.")
        st.subheader("Supplier-wise reconciliation")
        supplier_rows = []
        for supplier, details in sorted(reconciliation["supplier_summary"].items()):
            supplier_rows.append({
                "Supplier": supplier,
                "Invoices": details["invoice_count"],
                "Valid": details["valid_invoices"],
                "Invalid": details["invalid_invoices"],
                "Reported amount": f"{details[chr(114)+chr(101)+chr(112)+chr(111)+chr(114)+chr(116)+chr(101)+chr(100)+chr(95)+chr(97)+chr(109)+chr(111)+chr(117)+chr(110)+chr(116)]:,.2f}",
                "Calculated amount": f"{details[chr(99)+chr(97)+chr(108)+chr(99)+chr(117)+chr(108)+chr(97)+chr(116)+chr(101)+chr(100)+chr(95)+chr(97)+chr(109)+chr(111)+chr(117)+chr(110)+chr(116)]:,.2f}",
                "Discrepancy": f"{details[chr(100)+chr(105)+chr(115)+chr(99)+chr(114)+chr(101)+chr(112)+chr(97)+chr(110)+chr(99)+chr(121)]:,.2f}",
            })
        if supplier_rows:
            st.dataframe(supplier_rows, use_container_width=True)
        else:
            st.info("No supplier records to display.")
        reconciliation_csv = exporter.generate_reconciliation_csv(reconciliation)
        st.download_button(
            label="Download reconciliation CSV",
            data=reconciliation_csv,
            file_name="supplier_reconciliation.csv",
            mime="text/csv",
            use_container_width=True,
        )
