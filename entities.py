# src/domain/entities/ingredient.py
from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime

from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.unit_of_measure import UnitOfMeasure


@dataclass
class Ingredient:
    id: UUID
    name: str
    quantity: Quantity
    unit_of_measure: UnitOfMeasure
    category: str
    minimum_stock: Quantity
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @staticmethod
    def create(
        name: str,
        quantity: float,
        unit_of_measure: str,
        category: str,
        minimum_stock: float
    ) -> "Ingredient":
        return Ingredient(
            id=uuid4(),
            name=name,
            quantity=Quantity(quantity),
            unit_of_measure=UnitOfMeasure(unit_of_measure),
            category=category,
            minimum_stock=Quantity(minimum_stock),
            created_at=datetime.now()
        )
    
    def update_quantity(self, quantity: float) -> None:
        """Update the quantity of the ingredient"""
        self.quantity = Quantity(quantity)
        self.updated_at = datetime.now()
    
    def increase_quantity(self, amount: float) -> None:
        """Increase the quantity of the ingredient"""
        self.quantity = Quantity(self.quantity.value + amount)
        self.updated_at = datetime.now()
    
    def decrease_quantity(self, amount: float) -> None:
        """Decrease the quantity of the ingredient"""
        if self.quantity.value < amount:
            raise ValueError(f"Not enough {self.name} in stock. Current: {self.quantity.value}, Requested: {amount}")
        
        self.quantity = Quantity(self.quantity.value - amount)
        self.updated_at = datetime.now()
    
    def is_below_minimum(self) -> bool:
        """Check if the ingredient is below minimum stock level"""
        return self.quantity.value < self.minimum_stock.value


# src/domain/entities/recipe.py
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