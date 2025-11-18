# tests/integration/test_calculation.py
"""
Integration Tests for Polymorphic Calculation Models

These tests verify the polymorphic behavior of the Calculation model hierarchy.
Polymorphism in SQLAlchemy means that different calculation types (Addition,
Subtraction, etc.) can be treated uniformly while maintaining type-specific
behavior.

What Makes These Tests Polymorphic:
1. Factory Pattern: Calculation.create() returns different subclasses
2. Type Resolution: isinstance() checks verify correct subclass instantiation
3. Polymorphic Behavior: Each subclass implements get_result() differently
4. Common Interface: All calculations share the same methods/attributes

These tests demonstrate key OOP principles:
- Inheritance: Subclasses inherit from Calculation
- Polymorphism: Same interface, different implementations
- Encapsulation: Each class encapsulates its calculation logic
"""

import pytest
import uuid

from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)


# Helper function to create a dummy user_id for testing.
def dummy_user_id():
    """
    Generate a random UUID for testing purposes.
    
    In real tests with a database, you would create an actual user
    and use their ID. This helper is sufficient for unit-level testing
    of the calculation logic without database dependencies.
    """
    return uuid.uuid4()


# ============================================================================
# Tests for Individual Calculation Types
# ============================================================================

def test_addition_get_result():
    """
    Test that Addition.get_result returns the correct sum.
    
    This verifies that the Addition class correctly implements the
    polymorphic get_result() method for its specific operation.
    """
    addition = Addition(user_id=dummy_user_id(), a=10, b=5)
    result = addition.get_result()
    assert result == 15, f"Expected 15, got {result}"


def test_subtraction_get_result():
    """
    Test that Subtraction.get_result returns the correct difference.
    
    Subtraction performs sequential subtraction: first - second - third...
    """
    subtraction = Subtraction(user_id=dummy_user_id(), a=20, b=5)
    result = subtraction.get_result()
    assert result == 15, f"Expected 15, got {result}"


def test_multiplication_get_result():
    """
    Test that Multiplication.get_result returns the correct product.
    
    Multiplication multiplies all input numbers together.
    """
    multiplication = Multiplication(user_id=dummy_user_id(), a=3, b=4)
    result = multiplication.get_result()
    assert result == 12, f"Expected 12, got {result}"


def test_division_get_result():
    """
    Test that Division.get_result returns the correct quotient.
    
    """
    division = Division(user_id=dummy_user_id(), a=100, b=5)
    result = division.get_result()
    assert result == 20, f"Expected 20, got {result}"


def test_division_by_zero():
    """
    Test that Division.get_result raises ValueError when dividing by zero.
    
    This demonstrates EAFP (Easier to Ask for Forgiveness than Permission):
    We attempt the operation and catch the exception rather than checking
    beforehand.
    """
    division = Division(user_id=dummy_user_id(), a=50, b=0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        division.get_result()


def test_division_by_zero():
    """Test that Division.get_result raises ValueError when dividing by zero."""
    division = Division(user_id=dummy_user_id(), a=50, b=0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        division.get_result()


def test_addition_with_negative_numbers():
    """Test addition with negative numbers."""
    addition = Addition(user_id=dummy_user_id(), a=-5, b=-3)
    result = addition.get_result()
    assert result == -8


def test_subtraction_with_negative_result():
    """Test subtraction resulting in negative number."""
    subtraction = Subtraction(user_id=dummy_user_id(), a=5, b=10)
    result = subtraction.get_result()
    assert result == -5


def test_multiplication_with_zero():
    """Test multiplication with zero."""
    multiplication = Multiplication(user_id=dummy_user_id(), a=100, b=0)
    result = multiplication.get_result()
    assert result == 0


def test_division_with_zero_numerator():
    """Test division with zero as numerator."""
    division = Division(user_id=dummy_user_id(), a=0, b=5)
    result = division.get_result()
    assert result == 0.0


def test_addition_with_floats():
    """Test addition with floating point numbers."""
    addition = Addition(user_id=dummy_user_id(), a=10.5, b=5.3)
    result = addition.get_result()
    assert abs(result - 15.8) < 0.001

# ============================================================================
# Tests for Polymorphic Factory Pattern
# ============================================================================

def test_calculation_factory_addition():
    """
    Test the Calculation.create factory method for addition.
    
    This demonstrates polymorphism: The factory method returns a specific
    subclass (Addition) that can be used through the common Calculation
    interface.
    
    Key Polymorphic Concepts:
    1. Factory returns the correct subclass type
    2. The returned object behaves as both Calculation and Addition
    3. Type-specific behavior (get_result) works correctly
    """
    calc = Calculation.create(
        calculation_type='Add',
        user_id=dummy_user_id(),
        a=1,
        b=2
    )
    assert isinstance(calc, Addition), \
        "Factory did not return an Addition instance."
    assert isinstance(calc, Calculation), \
        "Addition should also be an instance of Calculation."
    assert calc.get_result() == 3, "Incorrect addition result."


def test_calculation_factory_subtraction():
    """
    Test the Calculation.create factory method for subtraction.
    
    Demonstrates that the factory pattern works consistently across
    different calculation types.
    """
    calc = Calculation.create(
        calculation_type='Subtract',
        user_id=dummy_user_id(),
        a=10,
        b=4
    )
    assert isinstance(calc, Subtraction), \
        "Factory did not return a Subtraction instance."
    assert calc.get_result() == 6, "Incorrect subtraction result."


def test_calculation_factory_multiplication():
    """
    Test the Calculation.create factory method for multiplication.
    """
    calc = Calculation.create(
        calculation_type='Multiply',
        user_id=dummy_user_id(),
        a=3,
        b=4
    )
    assert isinstance(calc, Multiplication), \
        "Factory did not return a Multiplication instance."
    assert calc.get_result() == 12, "Incorrect multiplication result."


def test_calculation_factory_division():
    """
    Test the Calculation.create factory method for division.
    """
    calc = Calculation.create(
        calculation_type='Divide',
        user_id=dummy_user_id(),
        a=100,
        b=5
    )
    assert isinstance(calc, Division), \
        "Factory did not return a Division instance."
    assert calc.get_result() == 20, "Incorrect division result."


def test_calculation_factory_invalid_type():
    """
    Test that Calculation.create raises a ValueError for unsupported types.
    
    This verifies that the factory pattern properly handles invalid inputs
    and provides clear error messages.
    """
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create(
            calculation_type='Modulus',
            user_id=dummy_user_id(),
            a=10,
            b=3
        )


def test_calculation_factory_case_insensitive():
    """
    Test that the factory is case-insensitive.
    
    The factory should accept 'Addition', 'ADDITION', 'addition', etc.
    """
    for calc_type in ['add', 'Add', 'ADD', 'AdD']:
        calc = Calculation.create(
            calculation_type=calc_type,
            user_id=dummy_user_id(),
            a=5,
            b=3
        )
        assert isinstance(calc, Addition), \
            f"Factory failed for case: {calc_type}"
        assert calc.get_result() == 8

def test_calculation_factory_division_by_zero():
    """Test that factory prevents division by zero at creation time."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        Calculation.create(
            calculation_type='Divide',
            user_id=dummy_user_id(),
            a=100,
            b=0
        )


def test_calculation_factory_stores_result():
    """Test that factory computes and stores result."""
    calc = Calculation.create(
        calculation_type='Multiply',
        user_id=dummy_user_id(),
        a=7,
        b=6
    )
    # Result should be pre-computed and stored
    assert calc.result == 42
    # And get_result() should return the same value
    assert calc.get_result() == 42



# ============================================================================
# Tests Demonstrating Polymorphic Behavior
# ============================================================================

def test_polymorphic_list_of_calculations():
    """
    Test that different calculation types can be stored in the same list.
    
    This demonstrates polymorphism: A list of Calculation objects can contain
    different subclasses, and each maintains its type-specific behavior.
    """
    user_id = dummy_user_id()
    
    # Create a list of different calculation types
    calculations = [
        Calculation.create('Add', user_id, a=10, b=5),
        Calculation.create('Subtract', user_id, a=10, b=3),
        Calculation.create('Multiply', user_id, a=4, b=5),
        Calculation.create('Divide', user_id, a=100, b=5),
    ]
    
    # Each calculation maintains its specific type
    assert isinstance(calculations[0], Addition)
    assert isinstance(calculations[1], Subtraction)
    assert isinstance(calculations[2], Multiplication)
    assert isinstance(calculations[3], Division)
    
    # All calculations share the same interface
    results = [calc.get_result() for calc in calculations]
    
    # Each produces its type-specific result
    assert results == [15, 7, 20, 20]


def test_polymorphic_method_calling():
    """
    Test that polymorphic methods work correctly.
    
    This demonstrates that you can call get_result() on any Calculation
    subclass and get the correct type-specific behavior.
    """
    user_id = dummy_user_id()
    
    # Create calculations dynamically based on type string
    calc_types = ['Add', 'Subtract', 'Multiply', 'Divide']
    expected_results = [12, 8, 20, 5]
    
    for calc_type, expected in zip(calc_types, expected_results):
        calc = Calculation.create(calc_type, user_id, a=10, b=2)
        result = calc.get_result()
        assert result == expected, \
            f"{calc_type} failed: expected {expected}, got {result}"

def test_base_calculation_get_result_not_implemented():
    """
    Test that calling get_result() on the base Calculation class raises NotImplementedError.
    
    This covers line 218 - the NotImplementedError in AbstractCalculation.get_result().
    The base class should never have get_result() called directly; it's meant to be
    overridden by subclasses.
    """

    calc = Calculation(user_id=dummy_user_id(), a=10, b=5)
    calc.type = 'calculation'  # Set the base type
    
    with pytest.raises(NotImplementedError, match="Subclasses must implement get_result"):
        calc.get_result()


def test_calculation_repr():
    """
    Test the __repr__ method of calculation objects.
    
    This covers line 223 - the __repr__ method.
    The repr should provide a useful string representation for debugging.
    """
    addition = Addition(user_id=dummy_user_id(), a=10, b=5)
    addition.result = addition.get_result()
    
    repr_string = repr(addition)
    
    # Verify the repr contains key information
    assert "Calculation" in repr_string
    assert "type=Add" in repr_string
    assert "a=10" in repr_string or "a=10.0" in repr_string
    assert "b=5" in repr_string or "b=5.0" in repr_string
    assert "result=15" in repr_string or "result=15.0" in repr_string


def test_multiple_calculation_repr():
    """
    Test __repr__ for different calculation types to ensure consistency.
    
    This provides additional coverage and verification of the __repr__ method
    across all calculation types.
    """
    user_id = dummy_user_id()
    
    calculations = [
        Addition(user_id=user_id, a=7, b=3),
        Subtraction(user_id=user_id, a=10, b=4),
        Multiplication(user_id=user_id, a=6, b=2),
        Division(user_id=user_id, a=20, b=5),
    ]
    
    # Compute results for all
    for calc in calculations:
        calc.result = calc.get_result()
    
    # Verify each has a meaningful repr
    reprs = [repr(calc) for calc in calculations]
    
    assert all("Calculation" in r for r in reprs)
    assert "type=Add" in reprs[0]
    assert "type=Subtract" in reprs[1]
    assert "type=Multiply" in reprs[2]
    assert "type=Divide" in reprs[3]