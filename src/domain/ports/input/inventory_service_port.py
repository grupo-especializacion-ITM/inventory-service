from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from uuid import UUID

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe


class InventoryServicePort(ABC):
    """Port for inventory service operations"""
    
    @abstractmethod
    async def create_ingredient(
        self,
        name: str,
        quantity: float,
        unit_of_measure: str,
        category: str,
        minimum_stock: float
    ) -> Ingredient:
        """Create a new ingredient"""
        pass
    
    @abstractmethod
    async def update_ingredient_stock(
        self,
        ingredient_id: UUID,
        quantity: float
    ) -> Ingredient:
        """Update the stock of an ingredient"""
        pass
    
    @abstractmethod
    async def add_ingredient_stock(
        self,
        ingredient_id: UUID,
        amount: float
    ) -> Ingredient:
        """Add stock to an ingredient"""
        pass
    
    @abstractmethod
    async def remove_ingredient_stock(
        self,
        ingredient_id: UUID,
        amount: float
    ) -> Ingredient:
        """Remove stock from an ingredient"""
        pass
    
    @abstractmethod
    async def validate_items_availability(
        self,
        items: List[Dict[str, any]]
    ) -> Dict[str, bool]:
        """
        Validate if items are available in the required quantities
        
        Each item in the list should have product_id and quantity
        Returns a dictionary mapping product IDs to availability status
        """
        pass
    
    @abstractmethod
    async def create_recipe(
        self,
        name: str,
        ingredients: List[Dict[str, any]],
        preparation_time: int,
        instructions: str
    ) -> Recipe:
        """Create a new recipe"""
        pass
    
    @abstractmethod
    async def update_recipe(
        self,
        recipe_id: UUID,
        name: Optional[str] = None,
        ingredients: Optional[List[Dict[str, any]]] = None,
        preparation_time: Optional[int] = None,
        instructions: Optional[str] = None
    ) -> Recipe:
        """Update a recipe"""
        pass
    
    @abstractmethod
    async def validate_recipe_availability(
        self,
        recipe_id: UUID,
        quantity: int = 1
    ) -> Dict[UUID, bool]:
        """
        Validate if all ingredients for a recipe are available in required quantities
        
        Returns a dictionary mapping ingredient IDs to availability status
        """
        pass