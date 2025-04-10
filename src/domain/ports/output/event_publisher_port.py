from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe


class EventPublisherPort(ABC):
    """Port for publishing events"""
    
    @abstractmethod
    async def publish_ingredient_created(self, ingredient: Ingredient) -> None:
        """Publish an ingredient created event"""
        pass
    
    @abstractmethod
    async def publish_ingredient_updated(self, ingredient: Ingredient) -> None:
        """Publish an ingredient updated event"""
        pass
    
    @abstractmethod
    async def publish_ingredient_stock_changed(
        self, 
        ingredient: Ingredient, 
        previous_quantity: float,
        change_type: str
    ) -> None:
        """Publish an ingredient stock changed event"""
        pass
    
    @abstractmethod
    async def publish_low_stock_alert(self, ingredient: Ingredient) -> None:
        """Publish a low stock alert event"""
        pass
    
    @abstractmethod
    async def publish_recipe_created(self, recipe: Recipe) -> None:
        """Publish a recipe created event"""
        pass
    
    @abstractmethod
    async def publish_recipe_updated(self, recipe: Recipe) -> None:
        """Publish a recipe updated event"""
        pass
    
    @abstractmethod
    async def publish_event(self, event_type: str, payload: Dict[str, Any], topic: Optional[str] = None) -> None:
        """Publish a generic event"""
        pass