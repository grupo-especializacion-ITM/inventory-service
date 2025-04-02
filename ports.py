# src/domain/ports/input/inventory_service_port.py
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


# src/domain/ports/input/inventory_query_port.py
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


# src/domain/ports/output/ingredient_repository_port.py
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


# src/domain/ports/output/recipe_repository_port.py
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


# src/domain/ports/output/event_publisher_port.py
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