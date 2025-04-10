from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class RecipeIngredient:
    ingredient_id: UUID
    name: str
    quantity: float
    unit_of_measure: str


@dataclass
class Recipe:
    id: UUID
    name: str
    ingredients: List[RecipeIngredient]
    preparation_time: int  # In minutes
    instructions: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @staticmethod
    def create(
        name: str,
        ingredients: List[RecipeIngredient],
        preparation_time: int,
        instructions: str
    ) -> "Recipe":
        return Recipe(
            id=uuid4(),
            name=name,
            ingredients=ingredients,
            preparation_time=preparation_time,
            instructions=instructions,
            created_at=datetime.now()
        )
    
    def update_ingredients(self, ingredients: List[RecipeIngredient]) -> None:
        """Update the ingredients in the recipe"""
        self.ingredients = ingredients
        self.updated_at = datetime.now()
    
    def update_instructions(self, instructions: str) -> None:
        """Update the preparation instructions"""
        self.instructions = instructions
        self.updated_at = datetime.now()
    
    def update_preparation_time(self, preparation_time: int) -> None:
        """Update the preparation time"""
        self.preparation_time = preparation_time
        self.updated_at = datetime.now()