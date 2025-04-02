# src/domain/aggregates/ingredient_aggregate.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from uuid import UUID

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe, RecipeIngredient
from src.domain.value_objects.quantity import Quantity
from src.domain.exceptions.domain_exceptions import InsufficientStockException


@dataclass
class IngredientAggregate:
    """Aggregate root for ingredients"""
    ingredient: Ingredient
    
    @classmethod
    def create_ingredient(
        cls,
        name: str,
        quantity: float,
        unit_of_measure: str,
        category: str,
        minimum_stock: float
    ) -> "IngredientAggregate":
        """Create a new ingredient aggregate"""
        ingredient = Ingredient.create(
            name=name,
            quantity=quantity,
            unit_of_measure=unit_of_measure,
            category=category,
            minimum_stock=minimum_stock
        )
        
        return cls(ingredient=ingredient)
    
    def update_stock(self, quantity: float) -> None:
        """Update the stock quantity of the ingredient"""
        self.ingredient.update_quantity(quantity)
    
    def add_stock(self, amount: float) -> None:
        """Add stock to the ingredient"""
        self.ingredient.increase_quantity(amount)
    
    def remove_stock(self, amount: float) -> None:
        """Remove stock from the ingredient"""
        try:
            self.ingredient.decrease_quantity(amount)
        except ValueError as e:
            raise InsufficientStockException(
                message=str(e),
                details={
                    "ingredient_id": str(self.ingredient.id),
                    "ingredient_name": self.ingredient.name,
                    "current_stock": self.ingredient.quantity.value,
                    "requested_amount": amount
                }
            )
    
    def check_availability(self, required_quantity: float) -> bool:
        """Check if there's enough stock to fulfill the required quantity"""
        return self.ingredient.quantity.value >= required_quantity
    
    def is_below_minimum_stock(self) -> bool:
        """Check if the ingredient is below minimum stock level"""
        return self.ingredient.is_below_minimum()


@dataclass
class RecipeWithIngredientsAggregate:
    """Aggregate that combines a recipe with its ingredients"""
    recipe: Recipe
    ingredients: Dict[UUID, Ingredient]
    
    def validate_availability(self) -> Dict[UUID, bool]:
        """
        Validate if all ingredients in the recipe are available in required quantities
        
        Returns a dictionary with ingredient IDs as keys and availability status as values
        """
        availability = {}
        
        for recipe_ingredient in self.recipe.ingredients:
            ingredient_id = recipe_ingredient.ingredient_id
            if ingredient_id not in self.ingredients:
                # Ingredient not found
                availability[ingredient_id] = False
                continue
            
            ingredient = self.ingredients[ingredient_id]
            required_quantity = recipe_ingredient.quantity
            
            # Check if units are compatible and convert if necessary
            if ingredient.unit_of_measure.unit != recipe_ingredient.unit_of_measure:
                try:
                    # Try to convert recipe quantity to ingredient's unit of measure
                    converted_quantity = ingredient.unit_of_measure.convert_to(
                        required_quantity, 
                        ingredient.unit_of_measure.unit
                    )
                    required_quantity = converted_quantity
                except ValueError:
                    # Units are incompatible
                    availability[ingredient_id] = False
                    continue
            
            # Check if there's enough stock
            availability[ingredient_id] = ingredient.quantity.value >= required_quantity
        
        return availability
    
    def consume_ingredients(self) -> None:
        """
        Consume the ingredients required by the recipe
        
        Raises InsufficientStockException if any ingredient is not available in sufficient quantity
        """
        # First, check availability
        availability = self.validate_availability()
        
        # If any ingredient is not available, raise an exception
        unavailable_ingredients = [
            self.recipe.ingredients[i].name
            for i, status in enumerate(availability.values())
            if not status
        ]
        
        if unavailable_ingredients:
            raise InsufficientStockException(
                message="Not enough ingredients in stock",
                details={"unavailable_ingredients": unavailable_ingredients}
            )
        
        # Consume all ingredients
        for recipe_ingredient in self.recipe.ingredients:
            ingredient_id = recipe_ingredient.ingredient_id
            ingredient = self.ingredients[ingredient_id]
            required_quantity = recipe_ingredient.quantity
            
            # Convert units if necessary
            if ingredient.unit_of_measure.unit != recipe_ingredient.unit_of_measure:
                required_quantity = ingredient.unit_of_measure.convert_to(
                    required_quantity, 
                    ingredient.unit_of_measure.unit
                )
            
            # Decrease the ingredient quantity
            ingredient.decrease_quantity(required_quantity)