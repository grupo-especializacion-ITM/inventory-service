# src/infrastructure/adapters/input/api/schemas.py
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator


class UnitOfMeasureEnum(str, Enum):
    # Weight units
    GRAM = "g"
    KILOGRAM = "kg"
    POUND = "lb"
    OUNCE = "oz"
    
    # Volume units
    MILLILITER = "ml"
    LITER = "l"
    GALLON = "gal"
    FLUID_OUNCE = "fl_oz"
    CUP = "cup"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    
    # Count units
    UNIT = "unit"
    PIECE = "piece"
    SLICE = "slice"
    WHOLE = "whole"


class IngredientCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    unit_of_measure: UnitOfMeasureEnum
    category: str = Field(..., min_length=1, max_length=100)
    minimum_stock: float = Field(..., ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Tomatoes",
                "quantity": 10.5,
                "unit_of_measure": "kg",
                "category": "Vegetables",
                "minimum_stock": 5.0
            }
        }


class IngredientUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[float] = Field(None, gt=0)
    unit_of_measure: Optional[UnitOfMeasureEnum] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    minimum_stock: Optional[float] = Field(None, ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Tomatoes",
                "quantity": 12.5,
                "minimum_stock": 6.0
            }
        }


class StockUpdateSchema(BaseModel):
    quantity: float = Field(..., gt=0)
    
    class Config:
        schema_extra = {
            "example": {
                "quantity": 15.0
            }
        }


class IngredientSchema(BaseModel):
    id: UUID
    name: str
    quantity: float
    unit_of_measure: str
    category: str
    minimum_stock: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Tomatoes",
                "quantity": 10.5,
                "unit_of_measure": "kg",
                "category": "Vegetables",
                "minimum_stock": 5.0,
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-02T12:00:00"
            }
        }


class RecipeIngredientSchema(BaseModel):
    ingredient_id: UUID
    name: str
    quantity: float
    unit_of_measure: str
    
    class Config:
        schema_extra = {
            "example": {
                "ingredient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Tomatoes",
                "quantity": 0.5,
                "unit_of_measure": "kg"
            }
        }


class RecipeIngredientCreateSchema(BaseModel):
    ingredient_id: UUID
    quantity: float = Field(..., gt=0)
    unit_of_measure: Optional[UnitOfMeasureEnum] = None
    
    class Config:
        schema_extra = {
            "example": {
                "ingredient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "quantity": 0.5,
                "unit_of_measure": "kg"
            }
        }


class RecipeCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    ingredients: List[RecipeIngredientCreateSchema] = Field(..., min_items=1)
    preparation_time: int = Field(..., gt=0)
    instructions: str = Field(..., min_length=10)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Tomato Soup",
                "ingredients": [
                    {
                        "ingredient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "quantity": 0.5,
                        "unit_of_measure": "kg"
                    },
                    {
                        "ingredient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                        "quantity": 1.0,
                        "unit_of_measure": "l"
                    }
                ],
                "preparation_time": 30,
                "instructions": "1. Chop tomatoes. 2. Boil water. 3. Mix all ingredients. 4. Simmer for 20 minutes."
            }
        }


class RecipeUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    ingredients: Optional[List[RecipeIngredientCreateSchema]] = Field(None, min_items=1)
    preparation_time: Optional[int] = Field(None, gt=0)
    instructions: Optional[str] = Field(None, min_length=10)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Improved Tomato Soup",
                "preparation_time": 25,
                "instructions": "1. Chop tomatoes. 2. Boil water. 3. Mix all ingredients. 4. Simmer for 15 minutes."
            }
        }


class RecipeSchema(BaseModel):
    id: UUID
    name: str
    ingredients: List[RecipeIngredientSchema]
    preparation_time: int
    instructions: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                "name": "Tomato Soup",
                "ingredients": [
                    {
                        "ingredient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "Tomatoes",
                        "quantity": 0.5,
                        "unit_of_measure": "kg"
                    },
                    {
                        "ingredient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                        "name": "Water",
                        "quantity": 1.0,
                        "unit_of_measure": "l"
                    }
                ],
                "preparation_time": 30,
                "instructions": "1. Chop tomatoes. 2. Boil water. 3. Mix all ingredients. 4. Simmer for 20 minutes.",
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-02T12:00:00"
            }
        }


class InventoryItemValidationSchema(BaseModel):
    product_id: str
    quantity: float = Field(..., gt=0)
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "quantity": 2.5
            }
        }


class InventoryValidationRequestSchema(BaseModel):
    items: List[InventoryItemValidationSchema] = Field(..., min_items=1)
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "quantity": 2.5
                    },
                    {
                        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                        "quantity": 1.0
                    }
                ]
            }
        }


class InventoryValidationResponseSchema(BaseModel):
    availability: Dict[str, bool]
    
    class Config:
        schema_extra = {
            "example": {
                "availability": {
                    "3fa85f64-5717-4562-b3fc-2c963f66afa6": True,
                    "3fa85f64-5717-4562-b3fc-2c963f66afa7": False
                }
            }
        }


class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, gt=0, le=1000)


class ErrorResponse(BaseModel):
    message: str
    details: Optional[Dict[str, Any]] = None