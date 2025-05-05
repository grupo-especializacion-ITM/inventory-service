from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.ports.input.inventory_service_port import InventoryServicePort
from src.domain.ports.input.inventory_query_port import InventoryQueryPort
from src.domain.exceptions.domain_exceptions import (
    DomainException,
    IngredientNotFoundException,
    RecipeNotFoundException,
    InsufficientStockException,
    InvalidQuantityException,
    InventoryOperationException
)
from src.application.services.inventory_service import InventoryService
from src.application.services.inventory_query_service import InventoryQueryService
from src.application.mappers.ingredient_mapper import IngredientMapper
from src.application.mappers.recipe_mapper import RecipeMapper
from src.infrastructure.adapters.output.repositories.ingredient_repository import IngredientRepository
from src.infrastructure.adapters.output.repositories.recipe_repository import RecipeRepository
from src.infrastructure.adapters.output.messaging.kafka_event_publisher import KafkaEventPublisher
from src.infrastructure.db.session import get_db_session
from src.infrastructure.adapters.input.api.schemas import (
    IngredientCreateSchema,
    IngredientUpdateSchema,
    StockUpdateSchema,
    IngredientSchema,
    RecipeCreateSchema,
    RecipeUpdateSchema,
    RecipeSchema,
    InventoryValidationRequestSchema,
    InventoryValidationResponseSchema,
    PaginationParams
)


class InventoryController:
    """Controller for inventory-related API endpoints"""
    
    @staticmethod
    async def get_inventory_service(session: AsyncSession = Depends(get_db_session)) -> InventoryServicePort:
        """Dependency for getting the inventory service"""
        ingredient_repository = IngredientRepository(session)
        recipe_repository = RecipeRepository(session)
        event_publisher = KafkaEventPublisher()
        
        return InventoryService(
            ingredient_repository=ingredient_repository,
            recipe_repository=recipe_repository,
            event_publisher=event_publisher
        )
    
    @staticmethod
    async def get_inventory_query_service(session: AsyncSession = Depends(get_db_session)) -> InventoryQueryPort:
        """Dependency for getting the inventory query service"""
        ingredient_repository = IngredientRepository(session)
        recipe_repository = RecipeRepository(session)
        
        return InventoryQueryService(
            ingredient_repository=ingredient_repository,
            recipe_repository=recipe_repository
        )
    
    # Ingredient endpoints
    
    @staticmethod
    async def create_ingredient(
        ingredient_data: IngredientCreateSchema,
        inventory_service: InventoryServicePort = Depends(get_inventory_service)
    ) -> IngredientSchema:
        """Create a new ingredient"""
        try:
            ingredient = await inventory_service.create_ingredient(
                name=ingredient_data.name,
                quantity=ingredient_data.quantity,
                unit_of_measure=ingredient_data.unit_of_measure.value,
                category=ingredient_data.category,
                minimum_stock=ingredient_data.minimum_stock
            )
            
            return IngredientMapper.to_dto(ingredient)
            
        except InventoryOperationException as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": e.message, "details": e.details}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_ingredient(
        ingredient_id: UUID,
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> IngredientSchema:
        """Get an ingredient by ID"""
        try:
            ingredient = await inventory_query_service.get_ingredient_by_id(ingredient_id)
            return IngredientMapper.to_dto(ingredient)
            
        except IngredientNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def update_ingredient(
        ingredient_id: UUID,
        ingredient_data: IngredientUpdateSchema,
        inventory_service: InventoryServicePort = Depends(get_inventory_service),
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> IngredientSchema:
        """Update an ingredient"""
        try:
            # Get the current ingredient
            current_ingredient = await inventory_query_service.get_ingredient_by_id(ingredient_id)
            
            # Update only the fields that are provided
            if ingredient_data.name is not None:
                current_ingredient.name = ingredient_data.name
            
            if ingredient_data.quantity is not None:
                await inventory_service.update_ingredient_stock(
                    ingredient_id=ingredient_id,
                    quantity=ingredient_data.quantity
                )
            
            if ingredient_data.unit_of_measure is not None:
                current_ingredient.unit_of_measure = ingredient_data.unit_of_measure.value
            
            if ingredient_data.category is not None:
                current_ingredient.category = ingredient_data.category
            
            if ingredient_data.minimum_stock is not None:
                current_ingredient.minimum_stock = ingredient_data.minimum_stock
            
            # TODO: This would be more efficient with a dedicated "update_ingredient" method
            # in the service, but we'll work with what we have.
            
            return IngredientMapper.to_dto(current_ingredient)
            
        except IngredientNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def update_ingredient_stock(
        ingredient_id: UUID,
        stock_data: StockUpdateSchema,
        inventory_service: InventoryServicePort = Depends(get_inventory_service)
    ) -> IngredientSchema:
        """Update the stock of an ingredient"""
        try:
            ingredient = await inventory_service.update_ingredient_stock(
                ingredient_id=ingredient_id,
                quantity=stock_data.quantity
            )
            
            return IngredientMapper.to_dto(ingredient)
            
        except IngredientNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def add_ingredient_stock(
        ingredient_id: UUID,
        stock_data: StockUpdateSchema,
        inventory_service: InventoryServicePort = Depends(get_inventory_service)
    ) -> IngredientSchema:
        """Add stock to an ingredient"""
        try:
            ingredient = await inventory_service.add_ingredient_stock(
                ingredient_id=ingredient_id,
                amount=stock_data.quantity
            )
            
            return IngredientMapper.to_dto(ingredient)
            
        except IngredientNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except InvalidQuantityException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def remove_ingredient_stock(
        ingredient_id: UUID,
        stock_data: StockUpdateSchema,
        inventory_service: InventoryServicePort = Depends(get_inventory_service)
    ) -> IngredientSchema:
        """Remove stock from an ingredient"""
        try:
            ingredient = await inventory_service.remove_ingredient_stock(
                ingredient_id=ingredient_id,
                amount=stock_data.quantity
            )
            
            return IngredientMapper.to_dto(ingredient)
            
        except IngredientNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except InsufficientStockException as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": e.message, "details": e.details}
            )
        except InvalidQuantityException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_ingredients_by_category(
        category: str,
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> List[IngredientSchema]:
        """Get all ingredients in a category"""
        try:
            ingredients = await inventory_query_service.get_ingredients_by_category(category)
            return IngredientMapper.to_dto_list(ingredients)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_ingredients_below_minimum_stock(
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> List[IngredientSchema]:
        """Get all ingredients below minimum stock level"""
        try:
            ingredients = await inventory_query_service.get_ingredients_below_minimum_stock()
            return IngredientMapper.to_dto_list(ingredients)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_all_ingredients(
        pagination: PaginationParams = Depends(),
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> List[IngredientSchema]:
        """Get all ingredients with pagination"""
        try:
            ingredients = await inventory_query_service.get_all_ingredients(
                skip=pagination.skip,
                limit=pagination.limit
            )
            return IngredientMapper.to_dto_list(ingredients)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def search_ingredients(
        query: str,
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> List[IngredientSchema]:
        """Search ingredients by name"""
        try:
            ingredients = await inventory_query_service.search_ingredients(query)
            return IngredientMapper.to_dto_list(ingredients)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    # Recipe endpoints
    
    @staticmethod
    async def create_recipe(
        recipe_data: RecipeCreateSchema,
        inventory_service: InventoryServicePort = Depends(get_inventory_service)
    ) -> RecipeSchema:
        """Create a new recipe"""
        try:
            # Prepare ingredients data
            ingredients = [
                {
                    "ingredient_id": str(ing.ingredient_id),
                    "quantity": ing.quantity,
                    "unit_of_measure": ing.unit_of_measure.value if ing.unit_of_measure else None
                }
                for ing in recipe_data.ingredients
            ]
            
            recipe = await inventory_service.create_recipe(
                name=recipe_data.name,
                ingredients=ingredients,
                preparation_time=recipe_data.preparation_time,
                instructions=recipe_data.instructions
            )
            
            return RecipeMapper.to_dto(recipe)
            
        except IngredientNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message, "details": e.details}
            )
        except InventoryOperationException as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": e.message, "details": e.details}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_recipe(
        recipe_id: UUID,
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> RecipeSchema:
        """Get a recipe by ID"""
        try:
            recipe = await inventory_query_service.get_recipe_by_id(recipe_id)
            return RecipeMapper.to_dto(recipe)
            
        except RecipeNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def update_recipe(
        recipe_id: UUID,
        recipe_data: RecipeUpdateSchema,
        inventory_service: InventoryServicePort = Depends(get_inventory_service)
    ) -> RecipeSchema:
        """Update a recipe"""
        try:
            update_args = {
                "recipe_id": recipe_id,
            }
            
            if recipe_data.name is not None:
                update_args["name"] = recipe_data.name
            
            if recipe_data.preparation_time is not None:
                update_args["preparation_time"] = recipe_data.preparation_time
            
            if recipe_data.instructions is not None:
                update_args["instructions"] = recipe_data.instructions
            
            if recipe_data.ingredients is not None:
                # Prepare ingredients data
                ingredients = [
                    {
                        "ingredient_id": str(ing.ingredient_id),
                        "quantity": ing.quantity,
                        "unit_of_measure": ing.unit_of_measure.value if ing.unit_of_measure else None
                    }
                    for ing in recipe_data.ingredients
                ]
                update_args["ingredients"] = ingredients
            
            recipe = await inventory_service.update_recipe(**update_args)
            
            return RecipeMapper.to_dto(recipe)
            
        except RecipeNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except IngredientNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message, "details": e.details}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_all_recipes(
        pagination: PaginationParams = Depends(),
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> List[RecipeSchema]:
        """Get all recipes with pagination"""
        try:
            recipes = await inventory_query_service.get_all_recipes(
                skip=pagination.skip,
                limit=pagination.limit
            )
            return RecipeMapper.to_dto_list(recipes)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def search_recipes(
        query: str,
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> List[RecipeSchema]:
        """Search recipes by name"""
        try:
            recipes = await inventory_query_service.search_recipes(query)
            return RecipeMapper.to_dto_list(recipes)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_recipes_by_ingredient(
        ingredient_id: UUID,
        inventory_query_service: InventoryQueryPort = Depends(get_inventory_query_service)
    ) -> List[RecipeSchema]:
        """Get all recipes that use a specific ingredient"""
        try:
            recipes = await inventory_query_service.get_recipes_by_ingredient(ingredient_id)
            return RecipeMapper.to_dto_list(recipes)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def validate_recipe_availability(
        recipe_id: UUID,
        quantity: int = Query(1, gt=0),
        inventory_service: InventoryServicePort = Depends(get_inventory_service)
    ) -> Dict[str, Any]:
        """Validate if all ingredients for a recipe are available"""
        try:
            availability = await inventory_service.validate_recipe_availability(
                recipe_id=recipe_id,
                quantity=quantity
            )
            
            return {
                "recipe_id": str(recipe_id),
                "quantity": quantity,
                "availability": {str(k): v for k, v in availability.items()},
                "all_available": all(availability.values())
            }
            
        except RecipeNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def validate_items_availability(
        validation_data: InventoryValidationRequestSchema,
        inventory_service: InventoryServicePort = Depends(get_inventory_service)
    ) -> InventoryValidationResponseSchema:
        """Validate if items are available in the required quantities"""
        try:
            items = [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity
                }
                for item in validation_data.items
            ]
            
            availability = await inventory_service.validate_items_availability(items)
            
            return InventoryValidationResponseSchema(availability=availability)
            
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )