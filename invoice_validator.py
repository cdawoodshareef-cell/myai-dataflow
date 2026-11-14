from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

def calculate_invoice_total(quantity, unit_price):
    return Decimal(str(quantity)) * Decimal(str(unit_price))

def validate_invoice_amount(quantity, unit_price, reported_total):
    try:
        qty = Decimal(str(quantity))
        price = Decimal(str(unit_price))
        reported = Decimal(str(reported_total))
        if not all(value.is_finite() for value in (qty, price, reported)):
            return False
        if qty <= 0 or price <= 0:
            return False
        calculated = calculate_invoice_total(qty, price)
        rounded = calculated.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return rounded == reported
    except (InvalidOperation, ValueError, TypeError):
        return False
