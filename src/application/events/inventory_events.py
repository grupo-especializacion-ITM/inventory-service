from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime
from uuid import uuid4

@dataclass(kw_only=True)
class Event:
    """Base event class"""
    event_id: UUID
    event_type: str
    timestamp: datetime
    version: str = "1.0"


@dataclass
class IngredientCreatedEvent(Event):
    """Event emitted when an ingredient is created"""
    ingredient_id: str
    name: str
    quantity: float
    unit_of_measure: str
    category: str
    
    @staticmethod
    def create(ingredient_id: str, name: str, quantity: float, 
              unit_of_measure: str, category: str) -> "IngredientCreatedEvent":
        
        
        return IngredientCreatedEvent(
            event_id=str(uuid4()),
            event_type="inventory.ingredient.created",
            timestamp=str(datetime.now()),
            ingredient_id=ingredient_id,
            name=name,
            quantity=quantity,
            unit_of_measure=unit_of_measure,
            category=category
        )


@dataclass
class IngredientUpdatedEvent(Event):
    """Event emitted when an ingredient is updated"""
    ingredient_id: str
    name: str
    quantity: float
    unit_of_measure: str
    category: str
    
    @staticmethod
    def create(ingredient_id: str, name: str, quantity: float,
              unit_of_measure: str, category: str) -> "IngredientUpdatedEvent":
        
        return IngredientUpdatedEvent(
            event_id=str(uuid4()),
            event_type="inventory.ingredient.updated",
            timestamp=str(datetime.now()),
            ingredient_id=ingredient_id,
            name=name,
            quantity=quantity,
            unit_of_measure=unit_of_measure,
            category=category
        )


@dataclass
class IngredientStockChangedEvent(Event):
    """Event emitted when an ingredient's stock quantity changes"""
    ingredient_id: str
    name: str
    previous_quantity: float
    new_quantity: float
    unit_of_measure: str
    change_type: str  # "increase", "decrease", "update"
    
    @staticmethod
    def create(ingredient_id: str, name: str, previous_quantity: float,
              new_quantity: float, unit_of_measure: str, 
              change_type: str) -> "IngredientStockChangedEvent":
        
        return IngredientStockChangedEvent(
            event_id=str(uuid4()),
            event_type="inventory.ingredient.stock_changed",
            timestamp=str(datetime.now()),
            ingredient_id=ingredient_id,
            name=name,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            unit_of_measure=unit_of_measure,
            change_type=change_type
        )


@dataclass
class LowStockAlertEvent(Event):
    """Event emitted when an ingredient falls below minimum stock level"""
    ingredient_id: str
    name: str
    current_quantity: float
    minimum_stock: float
    unit_of_measure: str
    
    @staticmethod
    def create(ingredient_id: str, name: str, current_quantity: float,
              minimum_stock: float, unit_of_measure: str) -> "LowStockAlertEvent":
        from uuid import uuid4
        
        return LowStockAlertEvent(
            event_id=str(uuid4()),
            event_type="inventory.ingredient.low_stock",
            timestamp=str(datetime.now()),
            ingredient_id=ingredient_id,
            name=name,
            current_quantity=current_quantity,
            minimum_stock=minimum_stock,
            unit_of_measure=unit_of_measure
        )


@dataclass
class RecipeCreatedEvent(Event):
    """Event emitted when a recipe is created"""
    recipe_id: str
    name: str
    ingredients: List[Dict[str, Any]]
    
    @staticmethod
    def create(recipe_id: str, name: str, 
              ingredients: List[Dict[str, Any]]) -> "RecipeCreatedEvent":
        
        return RecipeCreatedEvent(
            event_id=str(uuid4()),
            event_type="inventory.recipe.created",
            timestamp=str(datetime.now()),
            recipe_id=recipe_id,
            name=name,
            ingredients=ingredients
        )


@dataclass
class RecipeUpdatedEvent(Event):
    """Event emitted when a recipe is updated"""
    recipe_id: str
    name: str
    ingredients: List[Dict[str, Any]]
    
    @staticmethod
    def create(recipe_id: str, name: str,
              ingredients: List[Dict[str, Any]]) -> "RecipeUpdatedEvent":
        
        return RecipeUpdatedEvent(
            event_id=str(uuid4()),
            event_type="inventory.recipe.updated",
            timestamp=str(datetime.now()),
            recipe_id=recipe_id,
            name=name,
            ingredients=ingredients
        )


@dataclass
class InventoryValidationEvent(Event):
    """Event emitted when inventory validation is performed"""
    validation_id: str
    items: List[Dict[str, Any]]
    validation_result: Dict[str, bool]
    
    @staticmethod
    def create(validation_id: str, items: List[Dict[str, Any]],
              validation_result: Dict[str, bool]) -> "InventoryValidationEvent":
        from uuid import uuid4
        
        return InventoryValidationEvent(
            event_id=str(uuid4()),
            event_type="inventory.validation.performed",
            timestamp=str(datetime.now()),
            validation_id=validation_id,
            items=items,
            validation_result=validation_result
        )