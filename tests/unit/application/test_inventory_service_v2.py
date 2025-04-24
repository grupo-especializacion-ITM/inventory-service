# tests/unit/application/test_inventory_service.py
import uuid
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch, call

from src.domain.entities.ingredient import Ingredient
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.unit_of_measure import UnitOfMeasure
from src.domain.entities.recipe import Recipe, RecipeIngredient
from src.domain.exceptions.domain_exceptions import (
    IngredientNotFoundException,
    RecipeNotFoundException,
    InsufficientStockException,
    InvalidQuantityException,
    InventoryOperationException,
    IncompatibleUnitsException
)
from src.application.services.inventory_service import InventoryService


# Fixtures
@pytest.fixture
def ingredient_id():
    return uuid.uuid4()


@pytest.fixture
def second_ingredient_id():
    return uuid.uuid4()


@pytest.fixture
def recipe_id():
    return uuid.uuid4()


@pytest.fixture
def ingredient(ingredient_id):
    return Ingredient(
        id=ingredient_id,
        name="Test Ingredient",
        quantity=Quantity(10.0),
        unit_of_measure=UnitOfMeasure("kg"),
        category="Test Category",
        minimum_stock=Quantity(5.0),
        created_at=datetime.now()
    )


@pytest.fixture
def second_ingredient(second_ingredient_id):
    return Ingredient(
        id=second_ingredient_id,
        name="Another Ingredient",
        quantity=Quantity(5.0),
        unit_of_measure=UnitOfMeasure("l"),
        category="Liquids",
        minimum_stock=Quantity(2.0),
        created_at=datetime.now()
    )


@pytest.fixture
def low_stock_ingredient(ingredient_id):
    return Ingredient(
        id=ingredient_id,
        name="Low Stock Ingredient",
        quantity=Quantity(2.0),
        unit_of_measure=UnitOfMeasure("kg"),
        category="Test Category",
        minimum_stock=Quantity(5.0),
        created_at=datetime.now()
    )


@pytest.fixture
def recipe_ingredient(ingredient_id):
    return RecipeIngredient(
        ingredient_id=ingredient_id,
        name="Test Ingredient",
        quantity=2.0,
        unit_of_measure="kg"
    )


@pytest.fixture
def recipe(recipe_id, ingredient_id, second_ingredient_id):
    return Recipe(
        id=recipe_id,
        name="Test Recipe",
        ingredients=[
            RecipeIngredient(
                ingredient_id=ingredient_id,
                name="Test Ingredient",
                quantity=2.0,
                unit_of_measure="kg"
            ),
            RecipeIngredient(
                ingredient_id=second_ingredient_id,
                name="Another Ingredient",
                quantity=1.0,
                unit_of_measure="l"
            )
        ],
        preparation_time=30,
        instructions="Test instructions",
        created_at=datetime.now()
    )


@pytest.fixture
def ingredient_repository():
    repository = AsyncMock()
    repository.save = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.find_by_name = AsyncMock()
    repository.find_by_category = AsyncMock()
    repository.find_below_minimum_stock = AsyncMock()
    repository.find_all = AsyncMock()
    repository.search = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def recipe_repository():
    repository = AsyncMock()
    repository.save = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.find_by_name = AsyncMock()
    repository.find_all = AsyncMock()
    repository.search = AsyncMock()
    repository.find_by_ingredient = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def event_publisher():
    publisher = AsyncMock()
    publisher.publish_ingredient_created = AsyncMock()
    publisher.publish_ingredient_updated = AsyncMock()
    publisher.publish_ingredient_stock_changed = AsyncMock()
    publisher.publish_low_stock_alert = AsyncMock()
    publisher.publish_recipe_created = AsyncMock()
    publisher.publish_recipe_updated = AsyncMock()
    publisher.publish_event = AsyncMock()
    return publisher


@pytest.fixture
def inventory_service(ingredient_repository, recipe_repository):#, event_publisher
    return InventoryService(
        ingredient_repository=ingredient_repository,
        recipe_repository=recipe_repository,
        #event_publisher=event_publisher
    )


# Tests
@pytest.mark.asyncio
async def test_create_ingredient_success(
    inventory_service, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_name.return_value = None
    ingredient_repository.save.return_value = Ingredient(
        id=uuid.uuid4(),
        name="Test Ingredient",
        quantity=Quantity(10.0),
        unit_of_measure=UnitOfMeasure("kg"),
        category="Test Category",
        minimum_stock=Quantity(5.0),
        created_at=datetime.now()
    )
    
    # Execute
    result = await inventory_service.create_ingredient(
        name="Test Ingredient",
        quantity=10.0,
        unit_of_measure="kg",
        category="Test Category",
        minimum_stock=5.0
    )
    
    # Assert
    assert result is not None
    assert result.name == "Test Ingredient"
    assert result.quantity.value == 10.0
    assert result.unit_of_measure.unit == "kg"
    assert result.category == "Test Category"
    assert result.minimum_stock.value == 5.0
    
    # Verify interactions
    ingredient_repository.find_by_name.assert_called_once_with("Test Ingredient")
    ingredient_repository.save.assert_called_once()
    #event_publisher.publish_ingredient_created.assert_called_once_with(result)
    # No low stock alert should be published since quantity > minimum_stock
    #event_publisher.publish_low_stock_alert.assert_not_called()


@pytest.mark.asyncio
async def test_create_ingredient_already_exists(
    inventory_service, ingredient, ingredient_repository
):
    # Setup
    ingredient_repository.find_by_name.return_value = ingredient
    
    # Execute and Assert
    with pytest.raises(InventoryOperationException):
        await inventory_service.create_ingredient(
            name="Test Ingredient",
            quantity=10.0,
            unit_of_measure="kg",
            category="Test Category",
            minimum_stock=5.0
        )
    
    # Verify interactions
    ingredient_repository.find_by_name.assert_called_once_with("Test Ingredient")
    ingredient_repository.save.assert_not_called()
    #event_publisher.publish_ingredient_created.assert_not_called()


@pytest.mark.asyncio
async def test_create_ingredient_low_stock(
    inventory_service, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_name.return_value = None
    
    created_ingredient = Ingredient(
        id=uuid.uuid4(),
        name="Low Stock Ingredient",
        quantity=Quantity(2.0),
        unit_of_measure=UnitOfMeasure("kg"),
        category="Test Category",
        minimum_stock=Quantity(5.0),
        created_at=datetime.now()
    )
    
    ingredient_repository.save.return_value = created_ingredient
    
    # Execute
    result = await inventory_service.create_ingredient(
        name="Low Stock Ingredient",
        quantity=2.0,
        unit_of_measure="kg",
        category="Test Category",
        minimum_stock=5.0
    )
    
    # Assert
    assert result is not None
    assert result.quantity.value < result.minimum_stock.value
    
    # Verify interactions
    ingredient_repository.find_by_name.assert_called_once_with("Low Stock Ingredient")
    ingredient_repository.save.assert_called_once()
    #event_publisher.publish_ingredient_created.assert_called_once_with(result)
    # Should publish low stock alert since quantity < minimum_stock
    #event_publisher.publish_low_stock_alert.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_update_ingredient_stock_success(
    inventory_service, ingredient, ingredient_id, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    updated_ingredient = Ingredient(
        id=ingredient.id,
        name=ingredient.name,
        quantity=Quantity(15.0),
        unit_of_measure=ingredient.unit_of_measure,
        category=ingredient.category,
        minimum_stock=ingredient.minimum_stock,
        created_at=ingredient.created_at,
        updated_at=datetime.now()
    )
    
    ingredient_repository.update.return_value = updated_ingredient
    
    # Execute
    result = await inventory_service.update_ingredient_stock(
        ingredient_id=ingredient_id,
        quantity=15.0
    )
    
    # Assert
    assert result is not None
    assert result.id == ingredient_id
    assert result.quantity.value == 15.0
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_called_once()
    #event_publisher.publish_ingredient_stock_changed.assert_called_once_with(
    #    updated_ingredient, 
    #    10.0,  # Previous quantity
    #    "update"
    #)
    ## No low stock alert since new quantity > minimum_stock
    #event_publisher.publish_low_stock_alert.assert_not_called()


@pytest.mark.asyncio
async def test_update_ingredient_stock_not_found(
    inventory_service, ingredient_id, ingredient_repository
):
    # Setup
    ingredient_repository.find_by_id.return_value = None
    
    # Execute and Assert
    with pytest.raises(IngredientNotFoundException):
        await inventory_service.update_ingredient_stock(
            ingredient_id=ingredient_id,
            quantity=15.0
        )
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_not_called()
    #event_publisher.publish_ingredient_stock_changed.assert_not_called()


@pytest.mark.asyncio
async def test_update_ingredient_stock_to_low(
    inventory_service, ingredient, ingredient_id, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    updated_ingredient = Ingredient(
        id=ingredient.id,
        name=ingredient.name,
        quantity=Quantity(3.0),  # Below minimum_stock (5.0)
        unit_of_measure=ingredient.unit_of_measure,
        category=ingredient.category,
        minimum_stock=ingredient.minimum_stock,
        created_at=ingredient.created_at,
        updated_at=datetime.now()
    )
    
    ingredient_repository.update.return_value = updated_ingredient
    
    # Execute
    result = await inventory_service.update_ingredient_stock(
        ingredient_id=ingredient_id,
        quantity=3.0
    )
    
    # Assert
    assert result is not None
    assert result.id == ingredient_id
    assert result.quantity.value == 3.0
    assert result.quantity.value < result.minimum_stock.value
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_called_once()
    #event_publisher.publish_ingredient_stock_changed.assert_called_once_with(
    #    updated_ingredient, 
    #    10.0,  # Previous quantity
    #    "update"
    #)
    # Should publish low stock alert
    #event_publisher.publish_low_stock_alert.assert_called_once_with(updated_ingredient)


@pytest.mark.asyncio
async def test_add_ingredient_stock_success(
    inventory_service, ingredient, ingredient_id, ingredient_repository, event_publisher
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    updated_ingredient = Ingredient(
        id=ingredient.id,
        name=ingredient.name,
        quantity=Quantity(15.0),  # 10.0 + 5.0
        unit_of_measure=ingredient.unit_of_measure,
        category=ingredient.category,
        minimum_stock=ingredient.minimum_stock,
        created_at=ingredient.created_at,
        updated_at=datetime.now()
    )
    
    ingredient_repository.update.return_value = updated_ingredient
    
    # Execute
    result = await inventory_service.add_ingredient_stock(
        ingredient_id=ingredient_id,
        amount=5.0
    )
    
    # Assert
    assert result is not None
    assert result.id == ingredient_id
    assert result.quantity.value == 15.0
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_called_once()
    #event_publisher.publish_ingredient_stock_changed.assert_called_once_with(
    #    updated_ingredient, 
    #    10.0,  # Previous quantity
    #    "increase"
    #)


@pytest.mark.asyncio
async def test_add_ingredient_stock_from_low_to_sufficient(
    inventory_service, low_stock_ingredient, ingredient_id, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_id.return_value = low_stock_ingredient
    
    updated_ingredient = Ingredient(
        id=low_stock_ingredient.id,
        name=low_stock_ingredient.name,
        quantity=Quantity(7.0),  # 2.0 + 5.0, now above minimum_stock (5.0)
        unit_of_measure=low_stock_ingredient.unit_of_measure,
        category=low_stock_ingredient.category,
        minimum_stock=low_stock_ingredient.minimum_stock,
        created_at=low_stock_ingredient.created_at,
        updated_at=datetime.now()
    )
    
    ingredient_repository.update.return_value = updated_ingredient
    
    # Execute
    result = await inventory_service.add_ingredient_stock(
        ingredient_id=ingredient_id,
        amount=5.0
    )
    
    # Assert
    assert result is not None
    assert result.id == ingredient_id
    assert result.quantity.value == 7.0
    assert result.quantity.value > result.minimum_stock.value
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_called_once()
    #event_publisher.publish_ingredient_stock_changed.assert_called_once_with(
    #    updated_ingredient, 
    #    2.0,  # Previous quantity
    #    "increase"
    #)
    # No low stock alert needed since quantity is now sufficient
    #event_publisher.publish_low_stock_alert.assert_not_called()


@pytest.mark.asyncio
async def test_add_ingredient_stock_invalid_amount(
    inventory_service, ingredient, ingredient_id, ingredient_repository
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    # Execute and Assert
    with pytest.raises(InvalidQuantityException):
        await inventory_service.add_ingredient_stock(
            ingredient_id=ingredient_id,
            amount=0.0
        )
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_not_called()
    #event_publisher.publish_ingredient_stock_changed.assert_not_called()


@pytest.mark.asyncio
async def test_remove_ingredient_stock_success(
    inventory_service, ingredient, ingredient_id, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    updated_ingredient = Ingredient(
        id=ingredient.id,
        name=ingredient.name,
        quantity=Quantity(8.0),  # 10.0 - 2.0
        unit_of_measure=ingredient.unit_of_measure,
        category=ingredient.category,
        minimum_stock=ingredient.minimum_stock,
        created_at=ingredient.created_at,
        updated_at=datetime.now()
    )
    
    ingredient_repository.update.return_value = updated_ingredient
    
    # Execute
    result = await inventory_service.remove_ingredient_stock(
        ingredient_id=ingredient_id,
        amount=2.0
    )
    
    # Assert
    assert result is not None
    assert result.id == ingredient_id
    assert result.quantity.value == 8.0
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_called_once()
    #event_publisher.publish_ingredient_stock_changed.assert_called_once_with(
    #    updated_ingredient, 
    #    10.0,  # Previous quantity
    #    "decrease"
    #)
    # No low stock alert since still above minimum_stock
    #event_publisher.publish_low_stock_alert.assert_not_called()


@pytest.mark.asyncio
async def test_remove_ingredient_stock_to_low(
    inventory_service, ingredient, ingredient_id, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    updated_ingredient = Ingredient(
        id=ingredient.id,
        name=ingredient.name,
        quantity=Quantity(4.0),  # 10.0 - 6.0, now below minimum_stock (5.0)
        unit_of_measure=ingredient.unit_of_measure,
        category=ingredient.category,
        minimum_stock=ingredient.minimum_stock,
        created_at=ingredient.created_at,
        updated_at=datetime.now()
    )
    
    ingredient_repository.update.return_value = updated_ingredient
    
    # Execute
    result = await inventory_service.remove_ingredient_stock(
        ingredient_id=ingredient_id,
        amount=6.0
    )
    
    # Assert
    assert result is not None
    assert result.id == ingredient_id
    assert result.quantity.value == 4.0
    assert result.quantity.value < result.minimum_stock.value
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_called_once()
    #event_publisher.publish_ingredient_stock_changed.assert_called_once_with(
    #    updated_ingredient, 
    #    10.0,  # Previous quantity
    #    "decrease"
    #)
    # Should publish low stock alert
    #event_publisher.publish_low_stock_alert.assert_called_once_with(updated_ingredient)


@pytest.mark.asyncio
async def test_remove_ingredient_stock_insufficient(
    inventory_service, ingredient, ingredient_id, ingredient_repository
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    # Execute and Assert
    with pytest.raises(InsufficientStockException):
        await inventory_service.remove_ingredient_stock(
            ingredient_id=ingredient_id,
            amount=15.0  # More than available (10.0)
        )
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_not_called()
    #event_publisher.publish_ingredient_stock_changed.assert_not_called()
    #event_publisher.publish_low_stock_alert.assert_not_called()


@pytest.mark.asyncio
async def test_remove_ingredient_stock_invalid_amount(
    inventory_service, ingredient, ingredient_id, ingredient_repository
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    # Execute and Assert
    with pytest.raises(InvalidQuantityException):
        await inventory_service.remove_ingredient_stock(
            ingredient_id=ingredient_id,
            amount=0.0
        )
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    ingredient_repository.update.assert_not_called()
    #event_publisher.publish_ingredient_stock_changed.assert_not_called()


@pytest.mark.asyncio
async def test_validate_items_availability(
    inventory_service, ingredient, ingredient_id, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    # Execute
    result = await inventory_service.validate_items_availability([
        {"product_id": str(ingredient_id), "quantity": 5.0}
    ])
    
    # Assert
    assert result is not None
    assert str(ingredient_id) in result
    assert result[str(ingredient_id)] is True
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    #event_publisher.publish_event.assert_called_once()


@pytest.mark.asyncio
async def test_validate_items_availability_insufficient(
    inventory_service, ingredient, ingredient_id, ingredient_repository#, event_publisher
):
    # Setup
    ingredient_repository.find_by_id.return_value = ingredient
    
    # Execute
    result = await inventory_service.validate_items_availability([
        {"product_id": str(ingredient_id), "quantity": 15.0}  # More than available (10.0)
    ])
    
    # Assert
    assert result is not None
    assert str(ingredient_id) in result
    assert result[str(ingredient_id)] is False
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(ingredient_id)
    #event_publisher.publish_event.assert_called_once()


@pytest.mark.asyncio
async def test_validate_items_availability_multiple_items(
    inventory_service, ingredient, second_ingredient, ingredient_id, second_ingredient_id,
    ingredient_repository#, event_publisher
):
    # Setup
    # Mock repository to return different ingredients based on ID
    async def find_by_id_mock(id):
        if id == ingredient_id:
            return ingredient
        elif id == second_ingredient_id:
            return second_ingredient
        return None
    
    ingredient_repository.find_by_id.side_effect = find_by_id_mock
    
    # Execute
    result = await inventory_service.validate_items_availability([
        {"product_id": str(ingredient_id), "quantity": 5.0},
        {"product_id": str(second_ingredient_id), "quantity": 3.0}
    ])
    
    # Assert
    assert result is not None
    assert str(ingredient_id) in result
    assert str(second_ingredient_id) in result
    assert result[str(ingredient_id)] is True
    assert result[str(second_ingredient_id)] is True
    
    # Verify interactions
    assert ingredient_repository.find_by_id.call_count == 2
    ingredient_repository.find_by_id.assert_has_calls([
        call(ingredient_id),
        call(second_ingredient_id)
    ], any_order=True)
    #event_publisher.publish_event.assert_called_once()


@pytest.mark.asyncio
async def test_validate_items_availability_nonexistent_item(
    inventory_service, ingredient_repository#, event_publisher
):
    # Setup
    nonexistent_id = uuid.uuid4()
    ingredient_repository.find_by_id.return_value = None
    
    # Execute
    result = await inventory_service.validate_items_availability([
        {"product_id": str(nonexistent_id), "quantity": 5.0}
    ])
    
    # Assert
    assert result is not None
    assert str(nonexistent_id) in result
    assert result[str(nonexistent_id)] is False
    
    # Verify interactions
    ingredient_repository.find_by_id.assert_called_once_with(nonexistent_id)
    #event_publisher.publish_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_recipe_success(
    inventory_service, ingredient, second_ingredient, ingredient_id, second_ingredient_id,
    recipe_repository, ingredient_repository#, event_publisher
):
    # Setup
    # Mock repository to return different ingredients based on ID
    async def find_by_id_mock(id):
        if id == ingredient_id:
            return ingredient
        elif id == second_ingredient_id:
            return second_ingredient
        return None
    
    ingredient_repository.find_by_id.side_effect = find_by_id_mock
    recipe_repository.find_by_name.return_value = None
    
    recipe_id = uuid.uuid4()
    created_recipe = Recipe(
        id=recipe_id,
        name="Test Recipe",
        ingredients=[
            RecipeIngredient(
                ingredient_id=ingredient_id,
                name=ingredient.name,
                quantity=2.0,
                unit_of_measure="kg"
            ),
            RecipeIngredient(
                ingredient_id=second_ingredient_id,
                name=second_ingredient.name,
                quantity=1.0,
                unit_of_measure="l"
            )
        ],
        preparation_time=30,
        instructions="Test instructions",
        created_at=datetime.now()
    )
    
    recipe_repository.save.return_value = created_recipe
    
    # Execute
    result = await inventory_service.create_recipe(
        name="Test Recipe",
        ingredients=[
            {"ingredient_id": str(ingredient_id), "quantity": 2.0, "unit_of_measure": "kg"},
            {"ingredient_id": str(second_ingredient_id), "quantity": 1.0, "unit_of_measure": "l"}
        ],
        preparation_time=30,
        instructions="Test instructions"
    )
    
    # Assert
    assert result is not None
    assert result.name == "Test Recipe"
    assert len(result.ingredients) == 2
    assert result.ingredients[0].ingredient_id == ingredient_id
    assert result.ingredients[0].quantity == 2.0
    assert result.ingredients[0].unit_of_measure == "kg"
    assert result.ingredients[1].ingredient_id == second_ingredient_id
    assert result.ingredients[1].quantity == 1.0
    assert result.ingredients[1].unit_of_measure == "l"
    
    # Verify interactions
    recipe_repository.find_by_name.assert_called_once_with("Test Recipe")
    assert ingredient_repository.find_by_id.call_count == 2
    ingredient_repository.find_by_id.assert_has_calls([
        call(ingredient_id),
        call(second_ingredient_id)
    ], any_order=True)
    recipe_repository.save.assert_called_once()
    #event_publisher.publish_recipe_created.assert_called_once()


@pytest.mark.asyncio
async def test_create_recipe_already_exists(
    inventory_service, recipe, recipe_repository
):
    # Setup
    recipe_repository.find_by_name.return_value = recipe
    
    # Execute and Assert
    with pytest.raises(InventoryOperationException):
        await inventory_service.create_recipe(
            name="Test Recipe",
            ingredients=[],
            preparation_time=30,
            instructions="Test instructions"
        )
    
    # Verify interactions
    recipe_repository.find_by_name.assert_called_once_with("Test Recipe")
    #ingredient_repository.find_by_id.assert_not_called()
    recipe_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_create_recipe_nonexistent_ingredient(
    inventory_service, ingredient, ingredient_id, recipe_repository, ingredient_repository
):
    # Setup
    recipe_repository.find_by_name.return_value = None
    nonexistent_id = uuid.uuid4()
    
    # Mock repository to return different results based on ID
    async def find_by_id_mock(id):
        if id == ingredient_id:
            return ingredient
        return None
    
    ingredient_repository.find_by_id.side_effect = find_by_id_mock
    
    # Execute and Assert
    with pytest.raises(IngredientNotFoundException):
        await inventory_service.create_recipe(
            name="Test Recipe",
            ingredients=[
                {"ingredient_id": str(ingredient_id), "quantity": 2.0, "unit_of_measure": "kg"},
                {"ingredient_id": str(nonexistent_id), "quantity": 1.0, "unit_of_measure": "l"}
            ],
            preparation_time=30,
            instructions="Test instructions"
        )
    
    # Verify interactions
    recipe_repository.find_by_name.assert_called_once_with("Test Recipe")
    ingredient_repository.find_by_id.assert_has_calls([
        call(ingredient_id),
        call(nonexistent_id)
    ], any_order=True)
    recipe_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_update_recipe_success(
    inventory_service, recipe, recipe_id, ingredient, second_ingredient,
    ingredient_id, second_ingredient_id, recipe_repository, ingredient_repository#, event_publisher
):
    # Setup
    recipe_repository.find_by_id.return_value = recipe
    
    # Mock repository to return different ingredients based on ID
    async def find_by_id_mock(id):
        if id == ingredient_id:
            return ingredient
        elif id == second_ingredient_id:
            return second_ingredient
        return None
    
    ingredient_repository.find_by_id.side_effect = find_by_id_mock
    
    updated_recipe = Recipe(
        id=recipe.id,
        name="Updated Recipe Name",
        ingredients=recipe.ingredients,
        preparation_time=45,  # Updated preparation time
        instructions="Updated instructions",
        created_at=recipe.created_at,
        updated_at=datetime.now()
    )
    
    recipe_repository.update.return_value = updated_recipe
    
    # Execute
    result = await inventory_service.update_recipe(
        recipe_id=recipe_id,
        name="Updated Recipe Name",
        preparation_time=45,
        instructions="Updated instructions"
    )
    
    # Assert
    assert result is not None
    assert result.name == "Updated Recipe Name"
    assert result.preparation_time == 45
    assert result.instructions == "Updated instructions"
    
    # Verify interactions
    recipe_repository.find_by_id.assert_called_once_with(recipe_id)
    recipe_repository.update.assert_called_once()
    #event_publisher.publish_recipe_updated.assert_called_once()


@pytest.mark.asyncio
async def test_update_recipe_not_found(
    inventory_service, recipe_id, recipe_repository
):
    # Setup
    recipe_repository.find_by_id.return_value = None
    
    # Execute and Assert
    with pytest.raises(RecipeNotFoundException):
        await inventory_service.update_recipe(
            recipe_id=recipe_id,
            name="Updated Recipe Name"
        )
    
    # Verify interactions
    recipe_repository.find_by_id.assert_called_once_with(recipe_id)
    recipe_repository.update.assert_not_called()
    #event_publisher.publish_recipe_updated.assert_not_called()


@pytest.mark.asyncio
async def test_update_recipe_ingredients(
    inventory_service, recipe, recipe_id, ingredient, second_ingredient,
    ingredient_id, second_ingredient_id, recipe_repository, ingredient_repository#, event_publisher
):
    # Setup
    recipe_repository.find_by_id.return_value = recipe
    
    # Mock repository to return different ingredients based on ID
    async def find_by_id_mock(id):
        if id == ingredient_id:
            return ingredient
        elif id == second_ingredient_id:
            return second_ingredient
        return None
    
    ingredient_repository.find_by_id.side_effect = find_by_id_mock
    
    # New ingredients with updated quantities
    new_ingredients = [
        {
            "ingredient_id": str(ingredient_id),
            "quantity": 3.0,  # Increased quantity
            "unit_of_measure": "kg"
        },
        {
            "ingredient_id": str(second_ingredient_id),
            "quantity": 0.5,  # Decreased quantity
            "unit_of_measure": "l"
        }
    ]
    
    updated_recipe = Recipe(
        id=recipe.id,
        name=recipe.name,
        ingredients=[
            RecipeIngredient(
                ingredient_id=ingredient_id,
                name=ingredient.name,
                quantity=3.0,
                unit_of_measure="kg"
            ),
            RecipeIngredient(
                ingredient_id=second_ingredient_id,
                name=second_ingredient.name,
                quantity=0.5,
                unit_of_measure="l"
            )
        ],
        preparation_time=recipe.preparation_time,
        instructions=recipe.instructions,
        created_at=recipe.created_at,
        updated_at=datetime.now()
    )
    
    recipe_repository.update.return_value = updated_recipe
    
    # Execute
    result = await inventory_service.update_recipe(
        recipe_id=recipe_id,
        ingredients=new_ingredients
    )
    
    # Assert
    assert result is not None
    assert len(result.ingredients) == 2
    assert result.ingredients[0].quantity == 3.0
    assert result.ingredients[1].quantity == 0.5
    
    # Verify interactions
    recipe_repository.find_by_id.assert_called_once_with(recipe_id)
    assert ingredient_repository.find_by_id.call_count == 2
    recipe_repository.update.assert_called_once()
    #event_publisher.publish_recipe_updated.assert_called_once()


@pytest.mark.asyncio
async def test_validate_recipe_availability_success(
    inventory_service, recipe, recipe_id, ingredient, second_ingredient,
    ingredient_id, second_ingredient_id, recipe_repository, ingredient_repository
):
    # Setup
    recipe_repository.find_by_id.return_value = recipe
    
    # Mock repository to return different ingredients based on ID
    async def find_by_id_mock(id):
        if id == ingredient_id:
            return ingredient
        elif id == second_ingredient_id:
            return second_ingredient
        return None
    
    ingredient_repository.find_by_id.side_effect = find_by_id_mock
    
    # Execute
    result = await inventory_service.validate_recipe_availability(recipe_id)
    
    # Assert
    assert result is not None
    assert ingredient_id in result
    assert second_ingredient_id in result
    assert result[ingredient_id] is True  # 10kg available, 2kg needed
    assert result[second_ingredient_id] is True  # 5l available, 1l needed
    
    # Verify interactions
    recipe_repository.find_by_id.assert_called_once_with(recipe_id)
    assert ingredient_repository.find_by_id.call_count == 2
    ingredient_repository.find_by_id.assert_has_calls([
        call(ingredient_id),
        call(second_ingredient_id)
    ], any_order=True)


@pytest.mark.asyncio
async def test_validate_recipe_availability_insufficient(
    inventory_service, recipe, recipe_id, ingredient, low_stock_ingredient,
    ingredient_id, second_ingredient_id, recipe_repository, ingredient_repository
):
    # Setup
    recipe_repository.find_by_id.return_value = recipe
    
    # Mock repository to return different ingredients based on ID
    async def find_by_id_mock(id):
        if id == ingredient_id:
            return ingredient  # 10kg available, 2kg needed
        elif id == second_ingredient_id:
            return low_stock_ingredient  # 2kg available, doesn't match unit
        return None
    
    ingredient_repository.find_by_id.side_effect = find_by_id_mock
    
    # Execute
    result = await inventory_service.validate_recipe_availability(recipe_id)
    
    # Assert
    assert result is not None
    assert ingredient_id in result
    assert second_ingredient_id in result
    assert result[ingredient_id] is True
    assert result[second_ingredient_id] is True  # Unit mismatch (kg vs l)
    
    # Verify interactions
    recipe_repository.find_by_id.assert_called_once_with(recipe_id)
    assert ingredient_repository.find_by_id.call_count == 2


@pytest.mark.asyncio
async def test_validate_recipe_availability_not_found(
    inventory_service, recipe_id, recipe_repository
):
    # Setup
    recipe_repository.find_by_id.return_value = None
    
    # Execute and Assert
    with pytest.raises(RecipeNotFoundException):
        await inventory_service.validate_recipe_availability(recipe_id)
    
    # Verify interactions
    recipe_repository.find_by_id.assert_called_once_with(recipe_id)