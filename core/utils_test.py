
from decimal import Decimal
from utils import get_number_from_text

import pytest

import exceptions

def test_simple_decimal():
    number = get_number_from_text("123.45")
    
    assert number == Decimal('123.45')
    
def test_simple_decimal_negative():
    number = get_number_from_text("-123.45")
    
    assert number == Decimal('-123.45')
    
def test_decimal_thousand_sep():
    number = get_number_from_text("1,123.45")
    
    assert number == Decimal('1123.45')
   
def test_not_enogh_decimal():
    # checking that assertion error is raised
    with pytest.raises(exceptions.InputFileStructureError):
        number = get_number_from_text("123.4")