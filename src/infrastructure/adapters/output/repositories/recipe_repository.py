from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.ports.output.recipe_repository_port import RecipeRepositoryPort
from src.domain.entities.recipe import Recipe, RecipeIngredient
from src.infrastructure.db.models.recipe_model import RecipeModel, RecipeIngredientModel
from src.infrastructure.db.models.ingredient_model import IngredientModel


class RecipeRepository(RecipeRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, recipe: Recipe) -> Recipe:
        """Save a recipe to the repository"""
        # Create recipe model instance
        recipe_model = RecipeModel(
            id=recipe.id,
            name=recipe.name,
            preparation_time=recipe.preparation_time,
            instructions=recipe.instructions,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at
        )
        
        # Add recipe model to session
        self.session.add(recipe_model)
        await self.session.flush()  # Flush to get the ID
        
        # Create recipe ingredients
        for ingredient in recipe.ingredients:
            recipe_ingredient_model = RecipeIngredientModel(
                recipe_id=recipe.id,
                ingredient_id=ingredient.ingredient_id,
                quantity=ingredient.quantity,
                unit_of_measure=ingredient.unit_of_measure
            )
            self.session.add(recipe_ingredient_model)
        
        # Commit changes
        await self.session.commit()
        
        # Return the saved recipe
        return recipe
    
    async def find_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        """Find a recipe by its ID"""
        query = (
            select(RecipeModel)
            .options(selectinload(RecipeModel.ingredients))
            .where(RecipeModel.id == recipe_id)
        )
        result = await self.session.execute(query)
        recipe_model = result.scalars().first()
        
        if not recipe_model:
            return None
        
        return await self._model_to_entity(recipe_model)
    
    async def find_by_name(self, name: str) -> Optional[Recipe]:
        """Find a recipe by its name"""
        query = (
            select(RecipeModel)
            .options(selectinload(RecipeModel.ingredients))
            .where(func.lower(RecipeModel.name) == func.lower(name))
        )
        result = await self.session.execute(query)
        recipe_model = result.scalars().first()
        
        if not recipe_model:
            return None
        
        return await self._model_to_entity(recipe_model)
    
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Recipe]:
        """Find all recipes with pagination"""
        query = (
            select(RecipeModel)
            .options(selectinload(RecipeModel.ingredients))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        recipe_models = result.scalars().all()
        
        recipes = []
        for model in recipe_models:
            recipe = await self._model_to_entity(model)
            recipes.append(recipe)
        
        return recipes
    
    async def search(self, query: str) -> List[Recipe]:
        """Search recipes by name"""
        search_pattern = f"%{query}%"
        query = (
            select(RecipeModel)
            .options(selectinload(RecipeModel.ingredients))
            .where(RecipeModel.name.ilike(search_pattern))
        )
        result = await self.session.execute(query)
        recipe_models = result.scalars().all()
        
        recipes = []
        for model in recipe_models:
            recipe = await self._model_to_entity(model)
            recipes.append(recipe)
        
        return recipes
    
    async def find_by_ingredient(self, ingredient_id: UUID) -> List[Recipe]:
        """Find all recipes that use a specific ingredient"""
        query = (
            select(RecipeModel)
            .options(selectinload(RecipeModel.ingredients))
            .join(RecipeIngredientModel)
            .where(RecipeIngredientModel.ingredient_id == ingredient_id)
        )
        result = await self.session.execute(query)
        recipe_models = result.scalars().all()
        
        recipes = []
        for model in recipe_models:
            recipe = await self._model_to_entity(model)
            recipes.append(recipe)
        
        return recipes
    
    async def update(self, recipe: Recipe) -> Recipe:
        """Update an existing recipe"""
        # Fetch the existing recipe
        query = (
            select(RecipeModel)
            .options(selectinload(RecipeModel.ingredients))
            .where(RecipeModel.id == recipe.id)
        )
        result = await self.session.execute(query)
        recipe_model = result.scalars().first()
        
        if not recipe_model:
            raise ValueError(f"Recipe with ID {recipe.id} not found")
        
        # Update the recipe fields
        recipe_model.name = recipe.name
        recipe_model.preparation_time = recipe.preparation_time
        recipe_model.instructions = recipe.instructions
        recipe_model.updated_at = recipe.updated_at if recipe.updated_at else datetime.now()
        
        # Delete existing recipe ingredients
        delete_query = (
            select(RecipeIngredientModel)
            .where(RecipeIngredientModel.recipe_id == recipe.id)
        )
        delete_result = await self.session.execute(delete_query)
        existing_ingredients = delete_result.scalars().all()
        
        for ingredient in existing_ingredients:
            await self.session.delete(ingredient)
        
        await self.session.flush()
        
        # Create new recipe ingredients
        for ingredient in recipe.ingredients:
            recipe_ingredient_model = RecipeIngredientModel(
                recipe_id=recipe.id,
                ingredient_id=ingredient.ingredient_id,
                quantity=ingredient.quantity,
                unit_of_measure=ingredient.unit_of_measure
            )
            self.session.add(recipe_ingredient_model)
        
        # Commit changes
        await self.session.commit()
        
        # Return the updated recipe
        return recipe
    
    async def delete(self, recipe_id: UUID) -> None:
        """Delete a recipe"""
        query = (
            select(RecipeModel)
            .where(RecipeModel.id == recipe_id)
        )
        result = await self.session.execute(query)
        recipe_model = result.scalars().first()
        
        if recipe_model:
            await self.session.delete(recipe_model)
            await self.session.commit()
    
    async def _model_to_entity(self, model: RecipeModel) -> Recipe:
        """Convert a DB model to a domain entity"""
        # Convert recipe ingredients
        ingredients = []
        for ingredient_relation in model.ingredients:
            # Fetch the ingredient name from the ingredients table
            query = select(IngredientModel).where(IngredientModel.id == ingredient_relation.ingredient_id)
            result = await self.session.execute(query)
            ingredient_model = result.scalars().first()
            
            ingredient_name = ingredient_model.name if ingredient_model else "Unknown Ingredient"
            
            recipe_ingredient = RecipeIngredient(
                ingredient_id=ingredient_relation.ingredient_id,
                name=ingredient_name,
                quantity=ingredient_relation.quantity,
                unit_of_measure=ingredient_relation.unit_of_measure
            )
            ingredients.append(recipe_ingredient)
        
        # Create recipe entity
        return Recipe(
            id=model.id,
            name=model.name,
            ingredients=ingredients,
            preparation_time=model.preparation_time,
            instructions=model.instructions,
            created_at=model.created_at,
            updated_at=model.updated_at
        )