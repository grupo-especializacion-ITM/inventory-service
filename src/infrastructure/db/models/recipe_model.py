import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from src.infrastructure.db.base import Base


class RecipeModel(Base):
    __tablename__ = "recipes"
    __table_args__ = {'schema': 'inventory_service'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    preparation_time = Column(Integer, nullable=False)  # In minutes
    instructions = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    ingredients = relationship("RecipeIngredientModel", back_populates="recipe", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recipe {self.name}>"


class RecipeIngredientModel(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = {'schema': 'inventory_service'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("inventory_service.recipes.id"))
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("inventory_service.ingredients.id"))
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(String(50), nullable=False)
    
    # Relationships
    recipe = relationship("RecipeModel", back_populates="ingredients")
    ingredient = relationship("IngredientModel", back_populates="recipe_ingredients")
    
    def __repr__(self):
        return f"<RecipeIngredient {self.recipe_id}:{self.ingredient_id}>"