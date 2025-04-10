from typing import List, Optional
from uuid import UUID

from src.domain.ports.input.inventory_query_port import InventoryQueryPort
from src.domain.ports.output.ingredient_repository_port import IngredientRepositoryPort
from src.domain.ports.output.recipe_repository_port import RecipeRepositoryPort
from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe
from src.domain.exceptions.domain_exceptions import (
    IngredientNotFoundException,
    RecipeNotFoundException
)


class InventoryQueryService(InventoryQueryPort):
    def __init__(
        self,
        ingredient_repository: IngredientRepositoryPort,
        recipe_repository: RecipeRepositoryPort
    ):
        self.ingredient_repository = ingredient_repository
        self.recipe_repository = recipe_repository
    
    async def get_ingredient_by_id(self, ingredient_id: UUID) -> Ingredient:
        """Get an ingredient by its ID"""
        ingredient = await self.ingredient_repository.find_by_id(ingredient_id)
        if not ingredient:
            raise IngredientNotFoundException(
                message=f"Ingredient with ID {ingredient_id} not found"
            )
        
        return ingredient
    
    async def get_ingredients_by_category(self, category: str) -> List[Ingredient]:
        """Get all ingredients in a category"""
        return await self.ingredient_repository.find_by_category(category)
    
    async def get_ingredients_below_minimum_stock(self) -> List[Ingredient]:
        """Get all ingredients below minimum stock level"""
        return await self.ingredient_repository.find_below_minimum_stock()
    
    async def get_all_ingredients(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ingredient]:
        """Get all ingredients with pagination"""
        return await self.ingredient_repository.find_all(skip, limit)
    
    async def search_ingredients(self, query: str) -> List[Ingredient]:
        """Search ingredients by name"""
        return await self.ingredient_repository.search(query)
    
    async def get_recipe_by_id(self, recipe_id: UUID) -> Recipe:
        """Get a recipe by its ID"""
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(
                message=f"Recipe with ID {recipe_id} not found"
            )
        
        return recipe
    
    async def get_all_recipes(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Recipe]:
        """Get all recipes with pagination"""
        return await self.recipe_repository.find_all(skip, limit)
    
    async def search_recipes(self, query: str) -> List[Recipe]:
        """Search recipes by name"""
        return await self.recipe_repository.search(query)
    
    async def get_recipes_by_ingredient(self, ingredient_id: UUID) -> List[Recipe]:
        """Get all recipes that use a specific ingredient"""
        return await self.recipe_repository.find_by_ingredient(ingredient_id)