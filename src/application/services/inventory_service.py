from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from src.domain.ports.input.inventory_service_port import InventoryServicePort
from src.domain.ports.output.ingredient_repository_port import IngredientRepositoryPort
from src.domain.ports.output.recipe_repository_port import RecipeRepositoryPort
#from src.domain.ports.output.event_publisher_port import EventPublisherPort
from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe, RecipeIngredient
from src.domain.aggregates.ingredient_aggregate import IngredientAggregate, RecipeWithIngredientsAggregate
from src.domain.exceptions.domain_exceptions import (
    IngredientNotFoundException,
    RecipeNotFoundException,
    InsufficientStockException,
    InvalidQuantityException,
    InventoryOperationException
)
""" from src.application.events.inventory_events import (
    IngredientCreatedEvent,
    IngredientUpdatedEvent,
    IngredientStockChangedEvent,
    LowStockAlertEvent,
    RecipeCreatedEvent,
    RecipeUpdatedEvent,
    InventoryValidationEvent
) """


class InventoryService(InventoryServicePort):
    def __init__(
        self,
        ingredient_repository: IngredientRepositoryPort,
        recipe_repository: RecipeRepositoryPort,
        #event_publisher: EventPublisherPort
    ):
        self.ingredient_repository = ingredient_repository
        self.recipe_repository = recipe_repository
        #self.event_publisher = event_publisher
    
    async def create_ingredient(
        self,
        name: str,
        quantity: float,
        unit_of_measure: str,
        category: str,
        minimum_stock: float
    ) -> Ingredient:
        """Create a new ingredient"""
        # Check if ingredient with this name already exists
        existing = await self.ingredient_repository.find_by_name(name)
        if existing:
            raise InventoryOperationException(
                message=f"Ingredient with name '{name}' already exists",
                details={"existing_ingredient_id": str(existing.id)}
            )
        
        # Create ingredient aggregate
        ingredient_aggregate = IngredientAggregate.create_ingredient(
            name=name,
            quantity=quantity,
            unit_of_measure=unit_of_measure,
            category=category,
            minimum_stock=minimum_stock
        )
        
        # Save to repository
        saved_ingredient = await self.ingredient_repository.save(ingredient_aggregate.ingredient)
        
        # Publish event
        #await self.event_publisher.publish_ingredient_created(saved_ingredient)
        
        # Check if below minimum stock and publish alert if needed
        """ if ingredient_aggregate.is_below_minimum_stock():
            await self.event_publisher.publish_low_stock_alert(saved_ingredient) """
        
        return saved_ingredient
    
    async def update_ingredient_stock(
        self,
        ingredient_id: UUID,
        quantity: float
    ) -> Ingredient:
        """Update the stock of an ingredient"""
        # Find the ingredient
        ingredient = await self.ingredient_repository.find_by_id(ingredient_id)
        if not ingredient:
            raise IngredientNotFoundException(
                message=f"Ingredient with ID {ingredient_id} not found"
            )
        
        # Create aggregate
        ingredient_aggregate = IngredientAggregate(ingredient=ingredient)
        
        # Track previous quantity for event
        previous_quantity = ingredient.quantity.value
        
        # Update stock
        ingredient_aggregate.update_stock(quantity)
        
        # Save to repository
        updated_ingredient = await self.ingredient_repository.update(ingredient_aggregate.ingredient)
        
        # Publish stock changed event
        """ await self.event_publisher.publish_ingredient_stock_changed(
            updated_ingredient,
            previous_quantity,
            "update"
        ) """
        
        # Check if below minimum stock and publish alert if needed
        """ if ingredient_aggregate.is_below_minimum_stock():
            await self.event_publisher.publish_low_stock_alert(updated_ingredient) """
        
        return updated_ingredient
    
    async def add_ingredient_stock(
        self,
        ingredient_id: UUID,
        amount: float
    ) -> Ingredient:
        """Add stock to an ingredient"""
        # Find the ingredient
        ingredient = await self.ingredient_repository.find_by_id(ingredient_id)
        if not ingredient:
            raise IngredientNotFoundException(
                message=f"Ingredient with ID {ingredient_id} not found"
            )
        
        # Validate amount
        if amount <= 0:
            raise InvalidQuantityException(
                message="Amount to add must be greater than zero",
                details={"provided_amount": amount}
            )
        
        # Create aggregate
        ingredient_aggregate = IngredientAggregate(ingredient=ingredient)
        
        # Track previous quantity for event
        previous_quantity = ingredient.quantity.value
        
        # Add stock
        ingredient_aggregate.add_stock(amount)
        
        # Save to repository
        updated_ingredient = await self.ingredient_repository.update(ingredient_aggregate.ingredient)
        
        # Publish stock changed event
        """ await self.event_publisher.publish_ingredient_stock_changed(
            updated_ingredient,
            previous_quantity,
            "increase"
        ) """
        
        return updated_ingredient
    
    async def remove_ingredient_stock(
        self,
        ingredient_id: UUID,
        amount: float
    ) -> Ingredient:
        """Remove stock from an ingredient"""
        # Find the ingredient
        ingredient = await self.ingredient_repository.find_by_id(ingredient_id)
        if not ingredient:
            raise IngredientNotFoundException(
                message=f"Ingredient with ID {ingredient_id} not found"
            )
        
        # Validate amount
        if amount <= 0:
            raise InvalidQuantityException(
                message="Amount to remove must be greater than zero",
                details={"provided_amount": amount}
            )
        
        # Create aggregate
        ingredient_aggregate = IngredientAggregate(ingredient=ingredient)
        
        # Track previous quantity for event
        previous_quantity = ingredient.quantity.value
        
        try:
            # Remove stock
            ingredient_aggregate.remove_stock(amount)
            
            # Save to repository
            updated_ingredient = await self.ingredient_repository.update(ingredient_aggregate.ingredient)
            
            # Publish stock changed event
            """ await self.event_publisher.publish_ingredient_stock_changed(
                updated_ingredient,
                previous_quantity,
                "decrease"
            ) """
            
            # Check if below minimum stock and publish alert if needed
            """ if ingredient_aggregate.is_below_minimum_stock():
                await self.event_publisher.publish_low_stock_alert(updated_ingredient) """
            
            return updated_ingredient
            
        except InsufficientStockException as e:
            # Re-raise the exception to be handled by the controller
            raise e
    
    async def validate_items_availability(
        self,
        items: List[Dict[str, any]]
    ) -> Dict[str, bool]:
        """
        Validate if items are available in the required quantities
        
        Each item in the list should have product_id and quantity
        Returns a dictionary mapping product IDs to availability status
        """
        result = {}
        validation_id = uuid4()
        
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)
            
            if not product_id or not quantity:
                result[product_id] = False
                continue
            
            try:
                # Try to parse product_id as UUID
                ingredient_id = UUID(product_id)
                
                # Find the ingredient
                ingredient = await self.ingredient_repository.find_by_id(ingredient_id)
                if not ingredient:
                    result[product_id] = False
                    continue
                
                # Create aggregate
                ingredient_aggregate = IngredientAggregate(ingredient=ingredient)
                
                # Check availability
                result[product_id] = ingredient_aggregate.check_availability(quantity)
                
            except (ValueError, TypeError):
                # Invalid UUID or quantity
                result[product_id] = False
        
        # Publish validation event
        """ await self.event_publisher.publish_event(
            event_type="inventory.validation.performed",
            payload=InventoryValidationEvent.create(
                validation_id=validation_id,
                items=items,
                validation_result=result
            ).__dict__
        ) """
        
        return result
    
    async def create_recipe(
        self,
        name: str,
        ingredients: List[Dict[str, any]],
        preparation_time: int,
        instructions: str
    ) -> Recipe:
        """Create a new recipe"""
        # Check if recipe with this name already exists
        existing = await self.recipe_repository.find_by_name(name)
        if existing:
            raise InventoryOperationException(
                message=f"Recipe with name '{name}' already exists",
                details={"existing_recipe_id": str(existing.id)}
            )
        
        # Validate and prepare recipe ingredients
        recipe_ingredients = []
        for ing in ingredients:
            ingredient_id = UUID(ing.get("ingredient_id"))
            
            # Check if ingredient exists
            ingredient = await self.ingredient_repository.find_by_id(ingredient_id)
            if not ingredient:
                raise IngredientNotFoundException(
                    message=f"Ingredient with ID {ingredient_id} not found",
                    details={"ingredient_index": ingredients.index(ing)}
                )
            
            recipe_ingredient = RecipeIngredient(
                ingredient_id=ingredient_id,
                name=ingredient.name,
                quantity=float(ing.get("quantity")),
                unit_of_measure=ing.get("unit_of_measure", ingredient.unit_of_measure.unit)
            )
            recipe_ingredients.append(recipe_ingredient)
        
        # Create recipe
        recipe = Recipe.create(
            name=name,
            ingredients=recipe_ingredients,
            preparation_time=preparation_time,
            instructions=instructions
        )
        
        # Save to repository
        saved_recipe = await self.recipe_repository.save(recipe)
        
        # Prepare ingredient data for the event
        ingredients_data = [
            {
                "ingredient_id": str(ing.ingredient_id),
                "name": ing.name,
                "quantity": ing.quantity,
                "unit_of_measure": ing.unit_of_measure
            }
            for ing in saved_recipe.ingredients
        ]
        
        # Publish event
        #await self.event_publisher.publish_recipe_created(saved_recipe)
        
        return saved_recipe
    
    async def update_recipe(
        self,
        recipe_id: UUID,
        name: Optional[str] = None,
        ingredients: Optional[List[Dict[str, any]]] = None,
        preparation_time: Optional[int] = None,
        instructions: Optional[str] = None
    ) -> Recipe:
        """Update a recipe"""
        # Find the recipe
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(
                message=f"Recipe with ID {recipe_id} not found"
            )
        
        # Update fields that are provided
        if name is not None:
            recipe.name = name
        
        if preparation_time is not None:
            recipe.update_preparation_time(preparation_time)
        
        if instructions is not None:
            recipe.update_instructions(instructions)
        
        if ingredients is not None:
            # Validate and prepare recipe ingredients
            recipe_ingredients = []
            for ing in ingredients:
                ingredient_id = UUID(ing.get("ingredient_id"))
                
                # Check if ingredient exists
                ingredient = await self.ingredient_repository.find_by_id(ingredient_id)
                if not ingredient:
                    raise IngredientNotFoundException(
                        message=f"Ingredient with ID {ingredient_id} not found",
                        details={"ingredient_index": ingredients.index(ing)}
                    )
                
                recipe_ingredient = RecipeIngredient(
                    ingredient_id=ingredient_id,
                    name=ingredient.name,
                    quantity=float(ing.get("quantity")),
                    unit_of_measure=ing.get("unit_of_measure", ingredient.unit_of_measure.unit)
                )
                recipe_ingredients.append(recipe_ingredient)
            
            recipe.update_ingredients(recipe_ingredients)
        
        # Save to repository
        updated_recipe = await self.recipe_repository.update(recipe)
        
        # Publish event
        #await self.event_publisher.publish_recipe_updated(updated_recipe)
        
        return updated_recipe
    
    async def validate_recipe_availability(
        self,
        recipe_id: UUID,
        quantity: int = 1
    ) -> Dict[UUID, bool]:
        """
        Validate if all ingredients for a recipe are available in required quantities
        
        Returns a dictionary mapping ingredient IDs to availability status
        """
        # Find the recipe
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(
                message=f"Recipe with ID {recipe_id} not found"
            )
        
        # Get all ingredients needed for the recipe
        ingredient_ids = [ing.ingredient_id for ing in recipe.ingredients]
        ingredients = {}
        
        for ing_id in ingredient_ids:
            ingredient = await self.ingredient_repository.find_by_id(ing_id)
            if ingredient:
                ingredients[ing_id] = ingredient
        
        # Create recipe with ingredients aggregate
        recipe_with_ingredients = RecipeWithIngredientsAggregate(
            recipe=recipe,
            ingredients=ingredients
        )
        
        # Validate availability
        return recipe_with_ingredients.validate_availability()