from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

def generate_reconciliation_summary(column_names, data_rows):
    normalized = {name.strip().lower(): i for i, name in enumerate(column_names)}
    required = ["invoice number", "supplier name", "quantity", "unit price", "total amount"]
    missing = [name for name in required if name not in normalized]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    summary = {
        "total_invoices": len(data_rows),
        "valid_invoices": 0,
        "invalid_invoices": 0,
        "duplicate_invoices": 0,
        "total_reported_amount": Decimal("0.00"),
        "total_calculated_amount": Decimal("0.00"),
        "total_discrepancy": Decimal("0.00"),
        "supplier_summary": {},
    }
    seen = set()
    for row in data_rows:
        key = tuple(row)
        if key in seen:
            summary["duplicate_invoices"] += 1
            continue
        seen.add(key)
        supplier_value = str(row[normalized["supplier name"]]).strip() if normalized["supplier name"] < len(row) else ""
        supplier = supplier_value or "Unknown supplier"
        report = summary["supplier_summary"].setdefault(supplier, {"invoice_count": 0, "valid_invoices": 0, "invalid_invoices": 0, "reported_amount": Decimal("0.00"), "calculated_amount": Decimal("0.00"), "discrepancy": Decimal("0.00")})
        report["invoice_count"] += 1
        try:
            if not str(row[normalized["invoice number"]]).strip() or not supplier_value:
                raise InvalidOperation
            qty = Decimal(str(row[normalized["quantity"]]))
            price = Decimal(str(row[normalized["unit price"]]))
            reported = Decimal(str(row[normalized["total amount"]]))
            if not all(v.is_finite() for v in (qty, price, reported)) or qty <= 0 or price <= 0:
                raise InvalidOperation
            calculated = (qty * price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            difference = calculated - reported
            summary["total_reported_amount"] += reported
            summary["total_calculated_amount"] += calculated
            summary["total_discrepancy"] += difference
            report["reported_amount"] += reported
            report["calculated_amount"] += calculated
            report["discrepancy"] += difference
            if difference == 0:
                summary["valid_invoices"] += 1
                report["valid_invoices"] += 1
            else:
                summary["invalid_invoices"] += 1
                report["invalid_invoices"] += 1
        except (InvalidOperation, ValueError, TypeError, IndexError):
            summary["invalid_invoices"] += 1
            report["invalid_invoices"] += 1
    return summary
