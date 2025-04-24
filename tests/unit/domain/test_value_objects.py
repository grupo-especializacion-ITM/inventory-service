# tests/unit/domain/test_value_objects.py
import pytest
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.unit_of_measure import UnitOfMeasure, UnitType


# Tests for Quantity value object
def test_quantity_create_valid():
    """Test creating a valid quantity"""
    qty = Quantity(10.5)
    assert qty.value == 10.5


def test_quantity_create_zero():
    """Test creating a quantity of zero"""
    qty = Quantity(0.0)
    assert qty.value == 0.0


def test_quantity_create_negative():
    """Test creating a negative quantity raises ValueError"""
    with pytest.raises(ValueError):
        Quantity(-1.0)


def test_quantity_addition():
    """Test adding two quantities"""
    qty1 = Quantity(5.0)
    qty2 = Quantity(3.0)
    result = qty1 + qty2
    assert isinstance(result, Quantity)
    assert result.value == 8.0


def test_quantity_addition_with_number():
    """Test adding a number to a quantity"""
    qty = Quantity(5.0)
    result = qty + 3.0
    assert isinstance(result, Quantity)
    assert result.value == 8.0


def test_quantity_subtraction():
    """Test subtracting two quantities"""
    qty1 = Quantity(5.0)
    qty2 = Quantity(3.0)
    result = qty1 - qty2
    assert isinstance(result, Quantity)
    assert result.value == 2.0


def test_quantity_subtraction_with_number():
    """Test subtracting a number from a quantity"""
    qty = Quantity(5.0)
    result = qty - 3.0
    assert isinstance(result, Quantity)
    assert result.value == 2.0


def test_quantity_equality():
    """Test equality comparison of quantities"""
    qty1 = Quantity(5.0)
    qty2 = Quantity(5.0)
    qty3 = Quantity(3.0)
    
    assert qty1 == qty2
    assert qty1 != qty3
    assert qty1 == 5.0
    assert qty1 != 3.0


def test_quantity_comparison():
    """Test greater/less comparison of quantities"""
    qty1 = Quantity(5.0)
    qty2 = Quantity(3.0)
    
    assert qty1 > qty2
    assert qty2 < qty1
    assert qty1 > 3.0
    assert qty1 < 10.0


# Tests for UnitOfMeasure value object
def test_unit_of_measure_create_valid():
    """Test creating a valid unit of measure"""
    unit = UnitOfMeasure("kg")
    assert unit.unit == "kg"
    assert unit.unit_type == UnitType.WEIGHT


def test_unit_of_measure_create_invalid():
    """Test creating an invalid unit of measure"""
    with pytest.raises(ValueError):
        UnitOfMeasure("invalid_unit")


def test_unit_of_measure_compatibility():
    """Test checking compatibility between units"""
    kg = UnitOfMeasure("kg")
    g = UnitOfMeasure("g")
    ml = UnitOfMeasure("ml")
    
    assert kg.is_compatible_with(g)
    assert g.is_compatible_with(kg)
    assert not kg.is_compatible_with(ml)


def test_unit_of_measure_conversion():
    """Test converting between compatible units"""
    kg = UnitOfMeasure("kg")
    g = UnitOfMeasure("g")
    
    # 2 kg to g
    assert kg.convert_to(2.0, "g") == 2000.0
    
    # 2000 g to kg
    assert g.convert_to(2000.0, "kg") == 2.0


def test_unit_of_measure_conversion_incompatible():
    """Test attempting to convert between incompatible units"""
    kg = UnitOfMeasure("kg")
    
    with pytest.raises(ValueError):
        kg.convert_to(2.0, "ml")


def test_unit_of_measure_conversion_to_invalid_unit():
    """Test attempting to convert to an invalid unit"""
    kg = UnitOfMeasure("kg")
    
    with pytest.raises(ValueError):
        kg.convert_to(2.0, "invalid_unit")


