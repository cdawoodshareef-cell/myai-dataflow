
import json
import math


def validate_sales(raw_json):
    """Validate the sales field in a JSON record."""

    try:
        data = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError):
        return "INVALID JSON"

    if not isinstance(data, dict):
        return "INVALID: expected JSON object"

    if "sales" not in data:
        return "INVALID: sales field missing"

    sales = data["sales"]

    if type(sales) not in (int, float):
        return "INVALID: sales must be a number"

    if isinstance(sales, float) and not math.isfinite(sales):
        return "INVALID: sales must be finite"

    if sales < 0:
        return "INVALID: negative sales"

    return "VALID"


def validate_json_records(records):
    """Validate multiple JSON records together."""

    results = []

    for index, record in enumerate(records, start=1):
        result = validate_sales(record)

        results.append({
            "row": index,
            "status": result,
        })

    return results
