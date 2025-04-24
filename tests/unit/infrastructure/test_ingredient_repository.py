# tests/unit/infrastructure/adapters/output/repositories/test_ingredient_repository.py
import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch, call

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ingredient import Ingredient
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.unit_of_measure import UnitOfMeasure
from src.infrastructure.db.models.ingredient_model import IngredientModel
from src.infrastructure.adapters.output.repositories.ingredient_repository import IngredientRepository


@pytest.fixture
def ingredient_id():
    return uuid.uuid4()


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.delete = AsyncMock()
    return session


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
def ingredient_model(ingredient_id):
    return IngredientModel(
        id=ingredient_id,
        name="Test Ingredient",
        quantity=10.0,
        unit_of_measure="kg",
        category="Test Category",
        minimum_stock=5.0,
        created_at=datetime.now()
    )


@pytest.fixture
def ingredient_repository(mock_session):
    return IngredientRepository(mock_session)


@pytest.mark.asyncio
async def test_save_ingredient(ingredient_repository, mock_session, ingredient):
    # Execute
    result = await ingredient_repository.save(ingredient)
    
    # Assert
    assert result == ingredient
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_id(ingredient_repository, mock_session, ingredient_model, ingredient_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = ingredient_model
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await ingredient_repository.find_by_id(ingredient_id)
    
    # Assert
    assert result is not None
    assert result.id == ingredient_id
    assert result.name == "Test Ingredient"
    assert result.quantity.value == 10.0
    assert result.unit_of_measure.unit == "kg"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_id_not_found(ingredient_repository, mock_session, ingredient_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await ingredient_repository.find_by_id(ingredient_id)
    
    # Assert
    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_name(ingredient_repository, mock_session, ingredient_model):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = ingredient_model
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await ingredient_repository.find_by_name("Test Ingredient")
    
    # Assert
    assert result is not None
    assert result.name == "Test Ingredient"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_category(ingredient_repository, mock_session, ingredient_model):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [ingredient_model]
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await ingredient_repository.find_by_category("Test Category")
    
    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0].category == "Test Category"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_below_minimum_stock(ingredient_repository, mock_session, ingredient_model):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [ingredient_model]
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await ingredient_repository.find_below_minimum_stock()
    
    # Assert
    assert result is not None
    assert len(result) == 1
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_all(ingredient_repository, mock_session, ingredient_model):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [ingredient_model]
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await ingredient_repository.find_all(skip=0, limit=10)
    
    # Assert
    assert result is not None
    assert len(result) == 1
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_search(ingredient_repository, mock_session, ingredient_model):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [ingredient_model]
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await ingredient_repository.search("Test")
    
    # Assert
    assert result is not None
    assert len(result) == 1
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update(ingredient_repository, mock_session, ingredient, ingredient_model, ingredient_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = ingredient_model
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await ingredient_repository.update(ingredient)
    
    # Assert
    assert result == ingredient
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(ingredient_repository, mock_session, ingredient, ingredient_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute and Assert
    with pytest.raises(ValueError):
        await ingredient_repository.update(ingredient)
    
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete(ingredient_repository, mock_session, ingredient_model, ingredient_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = ingredient_model
    mock_session.execute.return_value = mock_result
    
    # Execute
    await ingredient_repository.delete(ingredient_id)
    
    # Assert
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(ingredient_repository, mock_session, ingredient_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute
    await ingredient_repository.delete(ingredient_id)
    
    # Assert
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_model_to_entity_conversion(ingredient_repository, ingredient_model):
    # Execute
    result = ingredient_repository._model_to_entity(ingredient_model)
    
    # Assert
    assert result is not None
    assert result.id == ingredient_model.id
    assert result.name == ingredient_model.name
    assert result.quantity.value == ingredient_model.quantity
    assert result.unit_of_measure.unit == ingredient_model.unit_of_measure
    assert result.category == ingredient_model.category
    assert result.minimum_stock.value == ingredient_model.minimum_stock