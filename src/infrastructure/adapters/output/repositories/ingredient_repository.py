from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.ports.output.ingredient_repository_port import IngredientRepositoryPort
from src.domain.entities.ingredient import Ingredient
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.unit_of_measure import UnitOfMeasure
from src.infrastructure.db.models.ingredient_model import IngredientModel


class IngredientRepository(IngredientRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, ingredient: Ingredient) -> Ingredient:
        """Save an ingredient to the repository"""
        # Create ingredient model instance
        ingredient_model = IngredientModel(
            id=ingredient.id,
            name=ingredient.name,
            quantity=ingredient.quantity.value,
            unit_of_measure=ingredient.unit_of_measure.unit,
            category=ingredient.category,
            minimum_stock=ingredient.minimum_stock.value,
            created_at=ingredient.created_at,
            updated_at=ingredient.updated_at
        )
        
        # Add ingredient model to session
        self.session.add(ingredient_model)
        
        # Commit changes
        await self.session.commit()
        
        # Return the saved ingredient
        return ingredient
    
    async def find_by_id(self, ingredient_id: UUID) -> Optional[Ingredient]:
        """Find an ingredient by its ID"""
        query = select(IngredientModel).where(IngredientModel.id == ingredient_id)
        result = await self.session.execute(query)
        ingredient_model = result.scalars().first()
        
        if not ingredient_model:
            return None
        
        return self._model_to_entity(ingredient_model)
    
    async def find_by_name(self, name: str) -> Optional[Ingredient]:
        """Find an ingredient by its name"""
        query = select(IngredientModel).where(func.lower(IngredientModel.name) == func.lower(name))
        result = await self.session.execute(query)
        ingredient_model = result.scalars().first()
        
        if not ingredient_model:
            return None
        
        return self._model_to_entity(ingredient_model)
    
    async def find_by_category(self, category: str) -> List[Ingredient]:
        """Find all ingredients in a category"""
        query = select(IngredientModel).where(func.lower(IngredientModel.category) == func.lower(category))
        result = await self.session.execute(query)
        ingredient_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in ingredient_models]
    
    async def find_below_minimum_stock(self) -> List[Ingredient]:
        """Find all ingredients below minimum stock level"""
        query = select(IngredientModel).where(IngredientModel.quantity < IngredientModel.minimum_stock)
        result = await self.session.execute(query)
        ingredient_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in ingredient_models]
    
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ingredient]:
        """Find all ingredients with pagination"""
        query = select(IngredientModel).offset(skip).limit(limit)
        result = await self.session.execute(query)
        ingredient_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in ingredient_models]
    
    async def search(self, query: str) -> List[Ingredient]:
        """Search ingredients by name"""
        search_pattern = f"%{query}%"
        query = select(IngredientModel).where(IngredientModel.name.ilike(search_pattern))
        result = await self.session.execute(query)
        ingredient_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in ingredient_models]
    
    async def update(self, ingredient: Ingredient) -> Ingredient:
        """Update an existing ingredient"""
        # Fetch the existing ingredient
        query = select(IngredientModel).where(IngredientModel.id == ingredient.id)
        result = await self.session.execute(query)
        ingredient_model = result.scalars().first()
        
        if not ingredient_model:
            raise ValueError(f"Ingredient with ID {ingredient.id} not found")
        
        # Update the ingredient fields
        ingredient_model.name = ingredient.name
        ingredient_model.quantity = ingredient.quantity.value
        ingredient_model.unit_of_measure = ingredient.unit_of_measure.unit
        ingredient_model.category = ingredient.category
        ingredient_model.minimum_stock = ingredient.minimum_stock.value
        ingredient_model.updated_at = ingredient.updated_at if ingredient.updated_at else datetime.now()
        
        # Commit changes
        await self.session.commit()
        
        # Return the updated ingredient
        return ingredient
    
    async def delete(self, ingredient_id: UUID) -> None:
        """Delete an ingredient"""
        query = select(IngredientModel).where(IngredientModel.id == ingredient_id)
        result = await self.session.execute(query)
        ingredient_model = result.scalars().first()
        
        if ingredient_model:
            await self.session.delete(ingredient_model)
            await self.session.commit()
    
    def _model_to_entity(self, model: IngredientModel) -> Ingredient:
        """Convert a DB model to a domain entity"""
        return Ingredient(
            id=model.id,
            name=model.name,
            quantity=Quantity(model.quantity),
            unit_of_measure=UnitOfMeasure(model.unit_of_measure),
            category=model.category,
            minimum_stock=Quantity(model.minimum_stock),
            created_at=model.created_at,
            updated_at=model.updated_at
        )