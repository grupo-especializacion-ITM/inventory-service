from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, Body, status

from domain.ports.input.inventory_service_port import InventoryServicePort
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

router = APIRouter(
    prefix=f"{settings.API_PREFIX}",
    tags=["Inventory"]
)

# Ingredient routes
ingredient_router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"]
)


@ingredient_router.post(
    "",
    response_model=IngredientSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Ingredient created successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Ingredient already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def create_ingredient(
    ingredient_data: IngredientCreateSchema = Body(...),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Create a new ingredient.
    
    - **name**: Name of the ingredient
    - **quantity**: Initial quantity
    - **unit_of_measure**: Unit of measure (g, kg, ml, etc.)
    - **category**: Category of the ingredient
    - **minimum_stock**: Minimum stock level
    """
    return await InventoryController.create_ingredient(ingredient_data, inventory_service)


@ingredient_router.get(
    "/{ingredient_id}",
    response_model=IngredientSchema,
    responses={
        status.HTTP_200_OK: {"description": "Ingredient details retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Ingredient not found"}
    }
)
async def get_ingredient(
    ingredient_id: UUID = Path(..., description="The ID of the ingredient to get"),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Get an ingredient by ID.
    
    - **ingredient_id**: UUID of the ingredient to retrieve
    """
    return await InventoryController.get_ingredient(ingredient_id, inventory_service)


@ingredient_router.patch(
    "/{ingredient_id}",
    response_model=IngredientSchema,
    responses={
        status.HTTP_200_OK: {"description": "Ingredient updated successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Ingredient not found"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def update_ingredient(
    ingredient_id: UUID = Path(..., description="The ID of the ingredient to update"),
    ingredient_data: IngredientUpdateSchema = Body(...),
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Update an ingredient.
    
    - **ingredient_id**: UUID of the ingredient to update
    - **ingredient_data**: Fields to update (all are optional)
    """
    return await InventoryController.update_ingredient(ingredient_id, ingredient_data, inventory_service, inventory_query_service)


@ingredient_router.put(
    "/{ingredient_id}/stock",
    response_model=IngredientSchema,
    responses={
        status.HTTP_200_OK: {"description": "Ingredient stock updated successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Ingredient not found"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def update_ingredient_stock(
    ingredient_id: UUID = Path(..., description="The ID of the ingredient to update"),
    stock_data: StockUpdateSchema = Body(...),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Update the stock of an ingredient (set to a specific value).
    
    - **ingredient_id**: UUID of the ingredient to update
    - **quantity**: New quantity
    """
    return await InventoryController.update_ingredient_stock(ingredient_id, stock_data, inventory_service)


@ingredient_router.post(
    "/{ingredient_id}/stock/add",
    response_model=IngredientSchema,
    responses={
        status.HTTP_200_OK: {"description": "Stock added successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Ingredient not found"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def add_ingredient_stock(
    ingredient_id: UUID = Path(..., description="The ID of the ingredient"),
    stock_data: StockUpdateSchema = Body(...),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Add stock to an ingredient.
    
    - **ingredient_id**: UUID of the ingredient
    - **quantity**: Quantity to add
    """
    return await InventoryController.add_ingredient_stock(ingredient_id, stock_data, inventory_service)


@ingredient_router.post(
    "/{ingredient_id}/stock/remove",
    response_model=IngredientSchema,
    responses={
        status.HTTP_200_OK: {"description": "Stock removed successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Ingredient not found"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Not enough stock or validation error"}
    }
)
async def remove_ingredient_stock(
    ingredient_id: UUID = Path(..., description="The ID of the ingredient"),
    stock_data: StockUpdateSchema = Body(...),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Remove stock from an ingredient.
    
    - **ingredient_id**: UUID of the ingredient
    - **quantity**: Quantity to remove
    """
    return await InventoryController.remove_ingredient_stock(ingredient_id, stock_data, inventory_service)


@ingredient_router.get(
    "",
    response_model=List[IngredientSchema],
    responses={
        status.HTTP_200_OK: {"description": "List of ingredients retrieved successfully"}
    }
)
async def get_all_ingredients(
    pagination: PaginationParams = Depends(),
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Get all ingredients with pagination.
    
    - **skip**: Number of ingredients to skip
    - **limit**: Maximum number of ingredients to return
    """
    return await InventoryController.get_all_ingredients(pagination, inventory_query_service)


@ingredient_router.get(
    "/search",
    response_model=List[IngredientSchema],
    responses={
        status.HTTP_200_OK: {"description": "Search results retrieved successfully"}
    }
)
async def search_ingredients(
    query: str = Query(..., description="Search query (ingredient name)"),
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Search ingredients by name.
    
    - **query**: Search query (ingredient name)
    """
    return await InventoryController.search_ingredients(query, inventory_query_service)


@ingredient_router.get(
    "/category/{category}",
    response_model=List[IngredientSchema],
    responses={
        status.HTTP_200_OK: {"description": "Ingredients in category retrieved successfully"}
    }
)
async def get_ingredients_by_category(
    category: str = Path(..., description="Category name"),
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Get all ingredients in a category.
    
    - **category**: Category name
    """
    return await InventoryController.get_ingredients_by_category(category, inventory_query_service)


@ingredient_router.get(
    "/low-stock",
    response_model=List[IngredientSchema],
    responses={
        status.HTTP_200_OK: {"description": "Low-stock ingredients retrieved successfully"}
    }
)
async def get_ingredients_below_minimum_stock(
    inventory_query_service: InventoryServicePort = Depends(InventoryController.get_inventory_query_service)
):
    """
    Get all ingredients below minimum stock level.
    """
    return InventoryController.get_ingredients_below_minimum_stock(inventory_query_service)


# Recipe routes
recipe_router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


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
    return InventoryController.get_recipe(recipe_id, inventory_query_service)


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
    return InventoryController.update_recipe(recipe_id, recipe_data, inventory_service)


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
    return InventoryController.get_all_recipes(pagination, inventory_query_service)


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
    return InventoryController.search_recipes(query, inventory_query_service)


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
    return InventoryController.get_recipes_by_ingredient(ingredient_id, inventory_query_service)


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
    return InventoryController.validate_recipe_availability(recipe_id, quantity, inventory_service)


# Validation routes
validation_router = APIRouter(
    prefix="/inventory",
    tags=["Inventory Validation"]
)


@validation_router.post(
    "/validate",
    response_model=InventoryValidationResponseSchema,
    responses={
        status.HTTP_200_OK: {"description": "Validation performed successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def validate_items_availability(
    validation_data: InventoryValidationRequestSchema = Body(...),
    inventory_service: InventoryServicePort = Depends(InventoryController.get_inventory_service)
):
    """
    Validate if items are available in the required quantities.
    
    - **items**: List of items with product IDs and quantities
    """
    return InventoryController.validate_items_availability(validation_data, inventory_service)


# Include all sub-routers
router.include_router(ingredient_router)
router.include_router(recipe_router)
router.include_router(validation_router)