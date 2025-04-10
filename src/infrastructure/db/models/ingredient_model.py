import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from src.infrastructure.db.base import Base


class IngredientModel(Base):
    __tablename__ = "ingredients"
    __table_args__ = {'schema': 'inventory_service'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    minimum_stock = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    recipe_ingredients = relationship("RecipeIngredientModel", back_populates="ingredient")
    
    def __repr__(self):
        return f"<Ingredient {self.name}>"