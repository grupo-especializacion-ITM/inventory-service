from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.ingredient import Ingredient


class IngredientRepositoryPort(ABC):
    """Port for ingredient repository operations"""
    
    @abstractmethod
    async def save(self, ingredient: Ingredient) -> Ingredient:
        """Save an ingredient to the repository"""
        pass
    
    @abstractmethod
    async def find_by_id(self, ingredient_id: UUID) -> Optional[Ingredient]:
        """Find an ingredient by its ID"""
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Ingredient]:
        """Find an ingredient by its name"""
        pass
    
    @abstractmethod
    async def find_by_category(self, category: str) -> List[Ingredient]:
        """Find all ingredients in a category"""
        pass
    
    @abstractmethod
    async def find_below_minimum_stock(self) -> List[Ingredient]:
        """Find all ingredients below minimum stock level"""
        pass
    
    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ingredient]:
        """Find all ingredients with pagination"""
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[Ingredient]:
        """Search ingredients by name"""
        pass
    
    @abstractmethod
    async def update(self, ingredient: Ingredient) -> Ingredient:
        """Update an existing ingredient"""
        pass
    
    @abstractmethod
    async def delete(self, ingredient_id: UUID) -> None:
        """Delete an ingredient"""
        pass
