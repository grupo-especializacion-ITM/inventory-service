from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.recipe import Recipe


class RecipeRepositoryPort(ABC):
    """Port for recipe repository operations"""
    
    @abstractmethod
    async def save(self, recipe: Recipe) -> Recipe:
        """Save a recipe to the repository"""
        pass
    
    @abstractmethod
    async def find_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        """Find a recipe by its ID"""
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Recipe]:
        """Find a recipe by its name"""
        pass
    
    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Recipe]:
        """Find all recipes with pagination"""
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[Recipe]:
        """Search recipes by name"""
        pass
    
    @abstractmethod
    async def find_by_ingredient(self, ingredient_id: UUID) -> List[Recipe]:
        """Find all recipes that use a specific ingredient"""
        pass
    
    @abstractmethod
    async def update(self, recipe: Recipe) -> Recipe:
        """Update an existing recipe"""
        pass
    
    @abstractmethod
    async def delete(self, recipe_id: UUID) -> None:
        """Delete a recipe"""
        pass