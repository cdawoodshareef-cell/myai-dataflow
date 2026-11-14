import pytest
from invoice_validator import validate_invoice_amount

@pytest.mark.parametrize("quantity,unit_price,reported_total,expected", [('-5', '250.00', '-1250.00', False), ('5', '-250.00', '-1250.00', False), ('0', '250.00', '0.00', False), ('5', '0', '0.00', False), (None, '250.00', '1250.00', False), ('5', None, '1250.00', False), ('5', '250.00', None, False), ('Infinity', '250.00', 'Infinity', False), ('5', 'Infinity', 'Infinity', False), ('5', '250.00', 'Infinity', False), ('12abc', '250.00', '3000.00', False), ('5', '25abc', '125.00', False), ('5', '250.00', '12abc', False), ('3', '0.335', '1.01', True)])
def test_invoice_edge_cases(quantity,unit_price,reported_total,expected):
    assert validate_invoice_amount(quantity,unit_price,reported_total) is expected
