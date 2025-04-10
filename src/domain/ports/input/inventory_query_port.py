from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe


class InventoryQueryPort(ABC):
    """Port for querying inventory"""
    
    @abstractmethod
    async def get_ingredient_by_id(self, ingredient_id: UUID) -> Ingredient:
        """Get an ingredient by its ID"""
        pass
    
    @abstractmethod
    async def get_ingredients_by_category(self, category: str) -> List[Ingredient]:
        """Get all ingredients in a category"""
        pass
    
    @abstractmethod
    async def get_ingredients_below_minimum_stock(self) -> List[Ingredient]:
        """Get all ingredients below minimum stock level"""
        pass
    
    @abstractmethod
    async def get_all_ingredients(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ingredient]:
        """Get all ingredients with pagination"""
        pass
    
    @abstractmethod
    async def search_ingredients(self, query: str) -> List[Ingredient]:
        """Search ingredients by name"""
        pass
    
    @abstractmethod
    async def get_recipe_by_id(self, recipe_id: UUID) -> Recipe:
        """Get a recipe by its ID"""
        pass
    
    @abstractmethod
    async def get_all_recipes(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Recipe]:
        """Get all recipes with pagination"""
        pass
    
    @abstractmethod
    async def search_recipes(self, query: str) -> List[Recipe]:
        """Search recipes by name"""
        pass
    
    @abstractmethod
    async def get_recipes_by_ingredient(self, ingredient_id: UUID) -> List[Recipe]:
        """Get all recipes that use a specific ingredient"""
        pass
