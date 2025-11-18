# tests/integration/test_calculation_schema.py
"""
Integration Tests for Calculation Pydantic Schemas

These tests verify that Pydantic schemas correctly validate calculation data
using the 'a' and 'b' operand design (not 'inputs' list).

Key Testing Concepts:
1. Valid Data: Ensure schemas accept correct data
2. Invalid Data: Ensure schemas reject incorrect data with clear messages
3. Edge Cases: Test boundary conditions
4. Business Rules: Verify domain-specific validation (e.g., no division by 0)
"""

import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.schemas.calculation import (
    CalculationType,
    CalculationBase,
    CalculationCreate,
    CalculationUpdate,
    CalculationRead
)


# ============================================================================
# Tests for CalculationType Enum
# ============================================================================

def test_calculation_type_enum_values():
    """Test that CalculationType enum has correct values."""
    assert CalculationType.ADD.value == "Add"
    assert CalculationType.SUBTRACT.value == "Subtract"
    assert CalculationType.MULTIPLY.value == "Multiply"
    assert CalculationType.DIVIDE.value == "Divide"


# ============================================================================
# Tests for CalculationBase Schema
# ============================================================================

def test_calculation_base_valid_addition():
    """Test CalculationBase with valid addition data."""
    data = {
        "type": "Add",
        "a": 10.5,
        "b": 3.0
    }
    calc = CalculationBase(**data)
    assert calc.type == CalculationType.ADD
    assert calc.a == 10.5
    assert calc.b == 3.0


def test_calculation_base_valid_subtraction():
    """Test CalculationBase with valid subtraction data."""
    data = {
        "type": "Subtract",
        "a": 20,
        "b": 5.5
    }
    calc = CalculationBase(**data)
    assert calc.type == CalculationType.SUBTRACT
    assert calc.a == 20
    assert calc.b == 5.5


def test_calculation_base_case_insensitive_type():
    """Test that calculation type is case-insensitive."""
    for type_variant in ["add", "Add", "ADD", "AdD"]:
        data = {"type": type_variant, "a": 1, "b": 2}
        calc = CalculationBase(**data)
        assert calc.type == CalculationType.ADD


def test_calculation_base_invalid_type():
    """Test that invalid calculation type raises ValidationError."""
    data = {
        "type": "Modulus",  # Invalid type
        "a": 10,
        "b": 3
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationBase(**data)
    
    errors = exc_info.value.errors()
    assert any("Type must be one of" in str(err) for err in errors)


def test_calculation_base_missing_operand_a():
    """Test that missing 'a' operand raises ValidationError."""
    data = {
        "type": "Add",
        "b": 5
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationBase(**data)
    
    errors = exc_info.value.errors()
    assert any("a" in str(err) for err in errors)


def test_calculation_base_missing_operand_b():
    """Test that missing 'b' operand raises ValidationError."""
    data = {
        "type": "Multiply",
        "a": 5
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationBase(**data)
    
    errors = exc_info.value.errors()
    assert any("b" in str(err) for err in errors)


def test_calculation_base_division_by_zero():
    """
    Test that division by zero is caught by schema validation.
    
    This demonstrates LBYL (Look Before You Leap): We check for the error
    condition before attempting the operation.
    """
    data = {
        "type": "Divide",
        "a": 100,
        "b": 0  # Division by zero
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationBase(**data)
    
    errors = exc_info.value.errors()
    assert any("Cannot divide by zero" in str(err) for err in errors)


def test_calculation_base_division_zero_numerator_ok():
    """Test that zero as numerator (a) is allowed."""
    data = {
        "type": "Divide",
        "a": 0,  # Zero numerator is valid
        "b": 5
    }
    calc = CalculationBase(**data)
    assert calc.a == 0
    assert calc.b == 5


def test_calculation_base_negative_numbers():
    """Test that negative numbers are accepted."""
    data = {
        "type": "Subtract",
        "a": -5,
        "b": -10
    }
    calc = CalculationBase(**data)
    assert calc.a == -5
    assert calc.b == -10


def test_calculation_base_large_numbers():
    """Test that large numbers are handled correctly."""
    data = {
        "type": "Multiply",
        "a": 1e10,
        "b": 1e10
    }
    calc = CalculationBase(**data)
    assert calc.a == 1e10
    assert calc.b == 1e10


# ============================================================================
# Tests for CalculationCreate Schema
# ============================================================================

def test_calculation_create_valid():
    """Test CalculationCreate with valid data."""
    user_id = uuid4()
    data = {
        "type": "Multiply",
        "a": 2,
        "b": 3,
        "user_id": str(user_id)
    }
    calc = CalculationCreate(**data)
    assert calc.type == CalculationType.MULTIPLY
    assert calc.a == 2
    assert calc.b == 3
    assert calc.user_id == user_id


def test_calculation_create_missing_user_id():
    """Test that CalculationCreate requires user_id."""
    data = {
        "type": "Add",
        "a": 1,
        "b": 2
        # Missing user_id
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    
    errors = exc_info.value.errors()
    assert any("user_id" in str(err) for err in errors)


def test_calculation_create_invalid_user_id():
    """Test that invalid UUID format raises ValidationError."""
    data = {
        "type": "Subtract",
        "a": 10,
        "b": 5,
        "user_id": "not-a-valid-uuid"
    }
    with pytest.raises(ValidationError):
        CalculationCreate(**data)


def test_calculation_create_with_division_by_zero():
    """Test that CalculationCreate validates division by zero."""
    user_id = uuid4()
    data = {
        "type": "Divide",
        "a": 10,
        "b": 0,
        "user_id": str(user_id)
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    
    errors = exc_info.value.errors()
    assert any("Cannot divide by zero" in str(err) for err in errors)


# ============================================================================
# Tests for CalculationUpdate Schema
# ============================================================================

def test_calculation_update_valid_both_fields():
    """Test CalculationUpdate with both fields."""
    data = {
        "a": 42,
        "b": 7
    }
    calc = CalculationUpdate(**data)
    assert calc.a == 42
    assert calc.b == 7


def test_calculation_update_only_a():
    """Test CalculationUpdate with only 'a' field."""
    data = {"a": 100}
    calc = CalculationUpdate(**data)
    assert calc.a == 100
    assert calc.b is None


def test_calculation_update_only_b():
    """Test CalculationUpdate with only 'b' field."""
    data = {"b": 50}
    calc = CalculationUpdate(**data)
    assert calc.a is None
    assert calc.b == 50


def test_calculation_update_empty_fails():
    """Test that CalculationUpdate requires at least one field."""
    data = {}
    with pytest.raises(ValidationError) as exc_info:
        CalculationUpdate(**data)
    
    errors = exc_info.value.errors()
    assert any("At least one field" in str(err) for err in errors)


def test_calculation_update_with_negative():
    """Test CalculationUpdate accepts negative numbers."""
    data = {"a": -25.5, "b": 10}
    calc = CalculationUpdate(**data)
    assert calc.a == -25.5
    assert calc.b == 10


# ============================================================================
# Tests for CalculationRead Schema
# ============================================================================

def test_calculation_read_valid():
    """Test CalculationRead with all required fields."""
    from datetime import datetime
    
    data = {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "type": "Add",
        "a": 10,
        "b": 5,
        "result": 15.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    calc = CalculationRead(**data)
    assert calc.result == 15.0
    assert calc.type == CalculationType.ADD
    assert calc.a == 10
    assert calc.b == 5


def test_calculation_read_missing_result():
    """Test that CalculationRead requires result field."""
    from datetime import datetime
    
    data = {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "type": "Multiply",
        "a": 2,
        "b": 3,
        # Missing result
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationRead(**data)
    
    errors = exc_info.value.errors()
    assert any("result" in str(err) for err in errors)


def test_calculation_read_missing_timestamps():
    """Test that CalculationRead requires timestamps."""
    data = {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "type": "Divide",
        "a": 100,
        "b": 5,
        "result": 20.0
        # Missing created_at and updated_at
    }
    with pytest.raises(ValidationError):
        CalculationRead(**data)


# ============================================================================
# Tests for Complex Validation Scenarios
# ============================================================================

def test_multiple_calculations_with_different_types():
    """
    Test that schemas correctly validate multiple calculations of
    different types.
    """
    user_id = uuid4()
    
    calcs_data = [
        {"type": "Add", "a": 1, "b": 2, "user_id": str(user_id)},
        {"type": "Subtract", "a": 10, "b": 3, "user_id": str(user_id)},
        {"type": "Multiply", "a": 2, "b": 4, "user_id": str(user_id)},
        {"type": "Divide", "a": 100, "b": 5, "user_id": str(user_id)},
    ]
    
    calcs = [CalculationCreate(**data) for data in calcs_data]
    
    assert len(calcs) == 4
    assert calcs[0].type == CalculationType.ADD
    assert calcs[1].type == CalculationType.SUBTRACT
    assert calcs[2].type == CalculationType.MULTIPLY
    assert calcs[3].type == CalculationType.DIVIDE


def test_schema_with_mixed_int_and_float():
    """Test that schemas accept mixed integers and floats."""
    data = {
        "type": "Add",
        "a": 100,      # int
        "b": 23.5      # float
    }
    calc = CalculationBase(**data)
    assert calc.a == 100
    assert calc.b == 23.5


def test_schema_type_coercion():
    """Test that Pydantic coerces compatible types."""
    data = {
        "type": "Multiply",
        "a": "10",     # String that can be converted to float
        "b": "5.5"     # String that can be converted to float
    }
    calc = CalculationBase(**data)
    assert isinstance(calc.a, float)
    assert isinstance(calc.b, float)
    assert calc.a == 10.0
    assert calc.b == 5.5