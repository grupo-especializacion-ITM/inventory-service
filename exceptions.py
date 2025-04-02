# src/domain/exceptions/domain_exceptions.py
from typing import Any, Dict, Optional


class DomainException(Exception):
    """Base exception for all domain exceptions"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class IngredientNotFoundException(DomainException):
    """Exception raised when an ingredient is not found"""
    pass


class RecipeNotFoundException(DomainException):
    """Exception raised when a recipe is not found"""
    pass


class InsufficientStockException(DomainException):
    """Exception raised when there's not enough stock of an ingredient"""
    pass


class InvalidQuantityException(DomainException):
    """Exception raised when an invalid quantity is provided"""
    pass


class IncompatibleUnitsException(DomainException):
    """Exception raised when incompatible units are used"""
    pass


class InventoryOperationException(DomainException):
    """Exception raised when an inventory operation fails"""
    pass


class RecipeValidationException(DomainException):
    """Exception raised when a recipe validation fails"""
    pass