# app/schemas/calculation.py
"""
Calculation Pydantic Schemas

This module defines Pydantic schemas for validating calculation data at the
API boundary. Pydantic provides automatic validation, serialization, and
documentation generation for FastAPI.

Key Concepts:
- Schemas define the shape of data coming in/out of the API
- Validation happens automatically before data reaches your code
- Field validators provide custom validation logic
- Model validators can validate across multiple fields
- ConfigDict controls schema behavior and documentation

Design Pattern: Data Transfer Objects (DTOs)
These schemas act as DTOs, defining contracts between API and clients.
"""

from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    field_validator
)
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class CalculationType(str, Enum):
    """
    Enumeration of valid calculation types.
    
    Using an Enum provides:
    1. Type safety: Only valid values can be used
    2. Auto-completion: IDEs can suggest valid values
    3. Documentation: Automatically appears in OpenAPI spec
    4. Validation: Pydantic automatically rejects invalid values
    
    Inheriting from str makes this a string enum, so values serialize
    naturally as strings in JSON.
    """
    ADD = "Add"
    SUBTRACT = "Subtract"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


class CalculationBase(BaseModel):
    """
    Base schema for calculation data.
    
    This schema defines the common fields that all calculation requests share.
    It's used as a base for more specific schemas (Create, Update, Response).
    
    Design Pattern: This follows the DRY (Don't Repeat Yourself) principle by
    defining common fields once and reusing them in other schemas.
    """
    a: float = Field(
        ...,
        description="First operand",
        examples=[10.5]
    )
    b: float = Field(
        ...,
        description="Second operand",
        examples=[3.0]
    )
    type: CalculationType = Field(
        ...,
        description="Type of calculation to perform",
        examples=["Add"]
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v):
        """
        Validate and normalize the calculation type.
        
        This validator ensures that the type is a string and converts it to
        lowercase for case-insensitive comparison. It runs BEFORE Pydantic's
        standard validation (mode="before").
        
        Args:
            v: The value to validate
            
        Returns:
            The normalized (lowercase) type value
            
        Raises:
            ValueError: If the type is not a valid calculation type
        """
        if isinstance(v, str):
            # Capitalize first letter for case-insensitive matching
            v = v.capitalize()
            allowed = {e.value for e in CalculationType}
            if v not in allowed:
                raise ValueError(
                    f"Type must be one of: {', '.join(sorted(allowed))}"
                )
        return v


    @model_validator(mode='after')
    def validate_division_by_zero(self):
        """
        Validate that division by zero is prevented.
        
        This is a model validator that runs AFTER all fields are validated.
        It can access multiple fields to perform cross-field validation.
        
        Returns:
            self: The validated model instance
            
        Raises:
            ValueError: If attempting to divide by zero
        """
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"a": 10.5, "b": 3, "type": "Add"},
                {"a": 100, "b": 2, "type": "Divide"}
            ]
        }
    )


class CalculationCreate(CalculationBase):
    """
    Schema for creating a new Calculation.
    
    This schema is used when a client wants to create a calculation.
    It includes the user_id to associate the calculation with a user.
    
    In a real application, the user_id would typically come from the
    authenticated user's session rather than the request body.
    """
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "a": 10.5,
                "b": 3,                
                "type": "Add",
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class CalculationUpdate(BaseModel):
    """
    Schema for updating an existing Calculation.
    
    This schema allows clients to update the inputs of an existing
    calculation. All fields are optional since partial updates are allowed.
    
    Note: The calculation type cannot be changed after creation. If you need
    a different type, create a new calculation.
    """
    a: Optional[float] = Field(
        None,
        description="Updated first operand",
        examples=[42.0]
    )
    b: Optional[float] = Field(
        None,
        description="Updated second operand",
        examples=[7.0]
    )

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationUpdate":
        """
        Validate the inputs if they are being updated.
        
        Returns:
            self: The validated model instance
            
        Raises:
            ValueError: If inputs has fewer than 2 numbers
        """
        if self.a is None and self.b is None:
            raise ValueError(
                "At least one field (a or b) must be provided for update"
            )
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"a": 42, "b": 7}
        }
    )



class CalculationRead(CalculationBase):
    """
    Schema for reading a Calculation from the database.
    
    This schema includes all the fields that are returned when reading
    a calculation, including database-generated fields like id, created_at,
    and the computed result.
    
    The from_attributes=True config allows this schema to be populated from
    SQLAlchemy model instances using model.from_orm(db_calculation).
    """
    id: UUID = Field(
        ...,
        description="Unique UUID of the calculation",
        examples=["123e4567-e89b-12d3-a456-426614174999"]
    )
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    created_at: datetime = Field(
        ...,
        description="Time when the calculation was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Time when the calculation was last updated"
    )
    result: float = Field(
        ...,
        description="Result of the calculation",
        examples=[15.5]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "Add",
                "a": 10.5,
                "b": 3,
                "result": 15.5,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    )
