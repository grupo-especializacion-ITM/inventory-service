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


# Validation routes
validation_router = APIRouter()


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
    return await InventoryController.validate_items_availability(validation_data=validation_data, inventory_service=inventory_service)