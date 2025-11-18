# app/models/calculation.py
"""
Calculation Models with Polymorphic Inheritance

This module demonstrates SQLAlchemy's polymorphic inheritance pattern, where
multiple calculation types (Addition, Subtraction, Multiplication, Division)
inherit from a base Calculation model. This is a powerful ORM feature that
allows different types of calculations to be stored in the same table while
maintaining type-specific behavior.

Polymorphic Inheritance Explained:
- Single Table Inheritance: All calculation types share one table
- Discriminator Column: The 'type' column determines which class to use
- Polymorphic Identity: Each subclass has a unique identifier
- Factory Pattern: Calculation.create() returns the appropriate subclass

This design pattern allows for:
1. Querying all calculations together: session.query(Calculation).all()
2. Automatic type resolution: SQLAlchemy returns the correct subclass
3. Type-specific behavior: Each subclass implements get_result() differently
4. Easy extensibility: Add new calculation types by creating new subclasses
"""

from datetime import datetime
import uuid
from typing import List
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr
from app.database import Base


class AbstractCalculation:
    """
    Abstract base class defining common attributes for all calculations
    and uses 'a' and 'b' fields for two operands.
    
    This class uses SQLAlchemy's @declared_attr decorator to define columns
    that will be shared across all calculation types. The @declared_attr
    decorator is necessary when defining columns in a mixin class.
    
    Design Pattern: This follows the Template Method pattern, where the
    abstract class defines the structure and subclasses provide specific
    implementations.
    """

    @declared_attr
    def __tablename__(cls):
        """All calculation types share the 'calculations' table"""
        return 'calculations'

    @declared_attr
    def id(cls):
        """Unique identifier for each calculation (UUID for distribution)"""
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )

    @declared_attr
    def user_id(cls):
        """
        Foreign key to the user who owns this calculation.
        
        CASCADE delete ensures calculations are deleted when user is deleted.
        Index improves query performance when filtering by user_id.
        """
        return Column(
            UUID(as_uuid=True),
            ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
            index=True
        )

    @declared_attr
    def type(cls):
        """
        Discriminator column for polymorphic inheritance.
        
        This column tells SQLAlchemy which subclass to instantiate when
        loading records from the database. Values include: 'addition',
        'subtraction', 'multiplication', 'division'.
        """
        return Column(
            String(50),
            nullable=False,
            index=True
        )

    @declared_attr
    def a(cls):
        """First operand"""
        return Column(
            Float,
            nullable=False
        )

    @declared_attr
    def b(cls):
        """Second operand"""
        return Column(
            Float,
            nullable=False
        )

    @declared_attr
    def result(cls):
        """
        The computed result of the calculation.
        
        Stored as Float to handle decimal values. Can be NULL initially
        and computed on-demand using get_result() method.
        """
        return Column(
            Float,
            nullable=True
        )

    @declared_attr
    def created_at(cls):
        """Timestamp when the calculation was created"""
        return Column(
            DateTime,
            default=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def updated_at(cls):
        """Timestamp when the calculation was last updated"""
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def user(cls):
        """
        Relationship to the User model.
        
        back_populates creates a bidirectional relationship, allowing access
        to user.calculations and calculation.user.
        """
        return relationship("User", back_populates="calculations")

    @classmethod
    def create(cls, calculation_type: str, user_id: uuid.UUID,
               a: float, b: float) -> "Calculation":
        """
        Factory method to create the appropriate calculation subclass.
        
        This implements the Factory Pattern, which provides a centralized way
        to create objects without specifying their exact class. The factory
        determines which subclass to instantiate based on calculation_type.
        
        Benefits of Factory Pattern:
        1. Encapsulation: Object creation logic is in one place
        2. Flexibility: Easy to add new calculation types
        3. Type Safety: Returns strongly-typed subclass instances
        
        Args:
            calculation_type: Type of calculation ('Add', 'Subtract', 'Multiply', 'Divide')
            user_id: UUID of the user creating the calculation
            a: First operand
            b: Second operand

        Returns:
            An instance of the appropriate Calculation subclass
            
        Raises:
            ValueError: If calculation_type is not supported
            
        Example:
            calc = Calculation.create('Add', user_id, 10, 5)
            assert isinstance(calc, Addition)
            assert calc.get_result() == 15
        """
        calculation_classes = {
            'add': Addition,
            'subtract': Subtraction,
            'multiply': Multiplication,
            'divide': Division,
        }
        calc_type_lower = calculation_type.lower()
        calculation_class = calculation_classes.get(calc_type_lower)

        if not calculation_class:
            raise ValueError(
                f"Unsupported calculation type: {calculation_type}. "
                f"Must be one of: Add, Subtract, Multiply, Divide. "
            )
        
        if calc_type_lower == 'divide' and b == 0:
            raise ValueError("Cannot divide by zero")
        
        calc = calculation_class(user_id=user_id, a=a, b=b)
        calc.result = calc.get_result()

        return calc
    
    

    def get_result(self) -> float:
        """
        Abstract method to compute the calculation result.
        
        Each subclass must implement this method with its specific logic.
        This follows the Template Method pattern where the interface is
        defined here but implementation is deferred to subclasses.
        
        Raises:
            NotImplementedError: If called on base class
        """
        raise NotImplementedError(
            "Subclasses must implement get_result() method"
        )

    def __repr__(self):
        return f"<Calculation(type={self.type}, a={self.a}, b={self.b}, result={self.result})>"


class Calculation(Base, AbstractCalculation):
    """
    Base calculation model with polymorphic configuration.
    
    This class combines SQLAlchemy's Base with our AbstractCalculation mixin
    and configures polymorphic inheritance through __mapper_args__.
    
    Polymorphic Configuration:
    - polymorphic_on: Specifies the discriminator column (type)
    - polymorphic_identity: The value stored for this base class
    
    When querying Calculation, SQLAlchemy automatically:
    1. Reads the 'type' column value
    2. Determines the appropriate subclass
    3. Returns an instance of that subclass
    """
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "calculation",
    }


class Addition(Calculation):
    """
    Addition calculation subclass.
    
    Polymorphic Identity: 'Add'
    Operation: a + b
    
    Example:
        add = Addition(user_id=user_id, a=10, b=5)
        result = add.get_result()  # Returns 15
    """
    __mapper_args__ = {"polymorphic_identity": "Add"}

    def get_result(self) -> float:

        return self.a + self.b


class Subtraction(Calculation):
    """
    Subtraction calculation subclass.
    
    Polymorphic Identity: 'Subtract'
    Operation: a - b
    
    Example:
        sub = Subtraction(user_id=user_id, a=10, b=3)
        result = sub.get_result()  # Returns 7
    """
    __mapper_args__ = {"polymorphic_identity": "Subtract"}

    def get_result(self) -> float:

        return self.a - self.b


class Multiplication(Calculation):
    """
    Multiplication calculation subclass.
    
    Polymorphic Identity: 'Multiply'
    Operation: a * b
    
    Example:
        mult = Multiplication(user_id=user_id, a=4, b=5)
        result = mult.get_result()  # Returns 20
    """
    __mapper_args__ = {"polymorphic_identity": "Multiply"}

    def get_result(self) -> float:
        
        return self.a * self.b


class Division(Calculation):
    """
    Division calculation subclass.
    
    Polymorphic Identity: 'Divide'
    Operation: a / b
    
    Example:
        div = Division(user_id=user_id, a=100, b=5)
        result = div.get_result()  # Returns 20.0
    
    Note: Division by zero is prevented in both the factory method
    and the get_result() method for safety.
    """
    __mapper_args__ = {"polymorphic_identity": "Divide"}

    def get_result(self) -> float:
        if self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self.a / self.b
