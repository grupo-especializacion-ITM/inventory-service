from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from src.domain.exceptions.domain_exceptions import (
    DomainException,
    IngredientNotFoundException,
    RecipeNotFoundException,
    InsufficientStockException,
    InvalidQuantityException,
    InventoryOperationException
)


logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """Set up error handlers for the application"""
    
    @app.exception_handler(IngredientNotFoundException)
    async def ingredient_not_found_exception_handler(request: Request, exc: IngredientNotFoundException):
        """Handle ingredient not found exceptions"""
        logger.error(f"Ingredient not found: {exc.message}")
        return JSONResponse(
            status_code=404,
            content={"message": exc.message, "details": exc.details}
        )
    
    @app.exception_handler(RecipeNotFoundException)
    async def recipe_not_found_exception_handler(request: Request, exc: RecipeNotFoundException):
        """Handle recipe not found exceptions"""
        logger.error(f"Recipe not found: {exc.message}")
        return JSONResponse(
            status_code=404,
            content={"message": exc.message, "details": exc.details}
        )
    
    @app.exception_handler(InsufficientStockException)
    async def insufficient_stock_exception_handler(request: Request, exc: InsufficientStockException):
        """Handle insufficient stock exceptions"""
        logger.error(f"Insufficient stock: {exc.message}")
        return JSONResponse(
            status_code=422,
            content={"message": exc.message, "details": exc.details}
        )
    
    @app.exception_handler(InvalidQuantityException)
    async def invalid_quantity_exception_handler(request: Request, exc: InvalidQuantityException):
        """Handle invalid quantity exceptions"""
        logger.error(f"Invalid quantity: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={"message": exc.message, "details": exc.details}
        )
    
    @app.exception_handler(InventoryOperationException)
    async def inventory_operation_exception_handler(request: Request, exc: InventoryOperationException):
        """Handle inventory operation exceptions"""
        logger.error(f"Inventory operation error: {exc.message}")
        return JSONResponse(
            status_code=409,
            content={"message": exc.message, "details": exc.details}
        )
    
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        """Handle general domain exceptions"""
        logger.error(f"Domain exception: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={"message": exc.message, "details": exc.details}
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.error(f"HTTP exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": str(exc.detail)}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation error",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )