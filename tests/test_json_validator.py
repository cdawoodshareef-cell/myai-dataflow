
import pytest

from json_validator import validate_sales, validate_json_records


@pytest.mark.parametrize(
    "raw_json, expected",
    [
        ('{"sales": 1250}', "VALID"),
        ('{"sales": 1250.50}', "VALID"),
        ('{"sales": 0}', "VALID"),
        ('{"sales": "1250.50"}',
         "INVALID: sales must be a number"),
        ('{"sales": null}',
         "INVALID: sales must be a number"),
        ('{"supplier": "ABC Traders"}',
         "INVALID: sales field missing"),
        ('{"sales": true}',
         "INVALID: sales must be a number"),
        ('{"sales": -100}',
         "INVALID: negative sales"),
        ('{"sales": }', "INVALID JSON"),
        ('[1250]', "INVALID: expected JSON object"),
    ],
)
def test_validate_sales(raw_json, expected):
    assert validate_sales(raw_json) == expected


def test_validate_multiple_records():
    records = [
        '{"sales": 1250}',
        '{"sales": "500"}',
        '{"supplier": "ABC Traders"}',
    ]

    expected = [
        {"row": 1, "status": "VALID"},
        {"row": 2, "status": "INVALID: sales must be a number"},
        {"row": 3, "status": "INVALID: sales field missing"},
    ]

    assert validate_json_records(records) == expected


def test_empty_records():
    assert validate_json_records([]) == []
