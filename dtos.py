# src/application/dtos/ingredient_dto.py
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class IngredientDTO:
    id: Optional[UUID] = None
    name: str = ""
    quantity: float = 0.0
    unit_of_measure: str = ""
    category: str = ""
    minimum_stock: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# src/application/dtos/recipe_dto.py
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime


@dataclass
class RecipeIngredientDTO:
    ingredient_id: Optional[UUID] = None
    name: str = ""
    quantity: float = 0.0
    unit_of_measure: str = ""


@dataclass
class RecipeDTO:
    id: Optional[UUID] = None
    name: str = ""
    ingredients: List[RecipeIngredientDTO] = None
    preparation_time: int = 0
    instructions: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.ingredients is None:
            self.ingredients = []