from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, Body, status

from src.domain.ports.input.inventory_service_port import InventoryServicePort
from src.infrastructure.adapters.input.api.inventory_controller import InventoryController
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
    PaginationParams,
    ErrorResponse
)
from src.infrastructure.config.settings import get_settings

settings = get_settings()


# Recipe routes
recipe_router = APIRouter()


@recipe_router.post(
    "",
    response_model=RecipeSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Recipe created successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Ingredient not found"},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Recipe already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def create_recipe(
    recipe_data: RecipeCreateSchema = Body(...),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Create a new recipe.
    
    - **name**: Name of the recipe
    - **ingredients**: List of ingredients with quantities
    - **preparation_time**: Preparation time in minutes
    - **instructions**: Preparation instructions
    """
    return await InventoryController.create_recipe(recipe_data, inventory_service)


@recipe_router.get(
    "/search",
    response_model=List[RecipeSchema],
    responses={
        status.HTTP_200_OK: {"description": "Search results retrieved successfully"}
    }
)
async def search_recipes(
    query: str = Query(..., description="Search query (recipe name)"),
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Search recipes by name.
    
    - **query**: Search query (recipe name)
    """
    return await InventoryController.search_recipes(query, inventory_query_service)


@recipe_router.get(
    "/{recipe_id}",
    response_model=RecipeSchema,
    responses={
        status.HTTP_200_OK: {"description": "Recipe details retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Recipe not found"}
    }
)
async def get_recipe(
    recipe_id: UUID = Path(..., description="The ID of the recipe to get"),
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Get a recipe by ID.
    
    - **recipe_id**: UUID of the recipe to retrieve
    """
    return await InventoryController.get_recipe(recipe_id, inventory_query_service)


@recipe_router.patch(
    "/{recipe_id}",
    response_model=RecipeSchema,
    responses={
        status.HTTP_200_OK: {"description": "Recipe updated successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Recipe not found"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def update_recipe(
    recipe_id: UUID = Path(..., description="The ID of the recipe to update"),
    recipe_data: RecipeUpdateSchema = Body(...),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Update a recipe.
    
    - **recipe_id**: UUID of the recipe to update
    - **recipe_data**: Fields to update (all are optional)
    """
    return await InventoryController.update_recipe(recipe_id, recipe_data, inventory_service)


@recipe_router.get(
    "/",
    response_model=List[RecipeSchema],
    responses={
        status.HTTP_200_OK: {"description": "List of recipes retrieved successfully"}
    }
)
async def get_all_recipes(
    pagination: PaginationParams = Depends(),
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Get all recipes with pagination.
    
    - **skip**: Number of recipes to skip
    - **limit**: Maximum number of recipes to return
    """
    return await InventoryController.get_all_recipes(pagination, inventory_query_service)


@recipe_router.get(
    "/by-ingredient/{ingredient_id}",
    response_model=List[RecipeSchema],
    responses={
        status.HTTP_200_OK: {"description": "Recipes using ingredient retrieved successfully"}
    }
)
async def get_recipes_by_ingredient(
    ingredient_id: UUID = Path(..., description="Ingredient ID"),
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Get all recipes that use a specific ingredient.
    
    - **ingredient_id**: UUID of the ingredient
    """
    return await InventoryController.get_recipes_by_ingredient(ingredient_id, inventory_query_service)


@recipe_router.get(
    "/{recipe_id}/availability",
    responses={
        status.HTTP_200_OK: {"description": "Availability checked successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Recipe not found"}
    }
)
async def validate_recipe_availability(
    recipe_id: UUID = Path(..., description="The ID of the recipe to check"),
    quantity: int = Query(1, gt=0, description="Number of servings"),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Check if all ingredients for a recipe are available in the required quantities.
    
    - **recipe_id**: UUID of the recipe to check
    - **quantity**: Number of servings (default: 1)
    """
    return await InventoryController.validate_recipe_availability(recipe_id, quantity, inventory_service)