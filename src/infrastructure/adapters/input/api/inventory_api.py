from fastapi import APIRouter

from infrastructure.adapters.input.api.routes.recipe_route import recipe_router
from infrastructure.adapters.input.api.routes.ingredient_route import ingredient_router
from infrastructure.adapters.input.api.routes.validation_route import validation_router
from src.infrastructure.config.settings import get_settings


settings = get_settings()

router = APIRouter(prefix=f"{settings.API_PREFIX}")

# Include all sub-routers
router.include_router(ingredient_router, tags=["Inventory"], prefix="/ingredients")
router.include_router(recipe_router, prefix="/recipes", tags=["Recipes"])
router.include_router(validation_router, prefix="/inventory", tags=["Inventory Validation"])