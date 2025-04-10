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