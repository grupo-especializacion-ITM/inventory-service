# tests/unit/infrastructure/adapters/output/repositories/test_recipe_repository.py
import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch, call

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.recipe import Recipe, RecipeIngredient
from src.infrastructure.db.models.recipe_model import RecipeModel, RecipeIngredientModel
from src.infrastructure.db.models.ingredient_model import IngredientModel
from src.infrastructure.adapters.output.repositories.recipe_repository import RecipeRepository


@pytest.fixture
def recipe_id():
    return uuid.uuid4()


@pytest.fixture
def ingredient_id():
    return uuid.uuid4()


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def recipe_ingredient(ingredient_id):
    return RecipeIngredient(
        ingredient_id=ingredient_id,
        name="Test Ingredient",
        quantity=2.0,
        unit_of_measure="kg"
    )


@pytest.fixture
def recipe(recipe_id, recipe_ingredient):
    return Recipe(
        id=recipe_id,
        name="Test Recipe",
        ingredients=[recipe_ingredient],
        preparation_time=30,
        instructions="Test instructions",
        created_at=datetime.now()
    )


@pytest.fixture
def recipe_model(recipe_id):
    return RecipeModel(
        id=recipe_id,
        name="Test Recipe",
        preparation_time=30,
        instructions="Test instructions",
        created_at=datetime.now()
    )


@pytest.fixture
def recipe_ingredient_model(recipe_id, ingredient_id):
    return RecipeIngredientModel(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id,
        quantity=2.0,
        unit_of_measure="kg"
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
def recipe_repository(mock_session):
    return RecipeRepository(mock_session)


@pytest.mark.asyncio
async def test_save_recipe(recipe_repository, mock_session, recipe):
    # Execute
    result = await recipe_repository.save(recipe)
    
    # Assert
    assert result == recipe
    assert mock_session.add.call_count >= 1
    mock_session.flush.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_id(recipe_repository, mock_session, recipe_model, recipe_ingredient_model, recipe_id, ingredient_model, ingredient_id):
    # Setup
    recipe_model.ingredients = [recipe_ingredient_model]
    
    mock_recipe_result = MagicMock()
    mock_recipe_result.scalars.return_value.first.return_value = recipe_model
    
    mock_ingredient_result = MagicMock()
    mock_ingredient_result.scalars.return_value.first.return_value = ingredient_model
    
    # Configure mock_session.execute to return different results based on query
    def mock_execute_side_effect(query, *args, **kwargs):
        # If it's querying for recipe
        if isinstance(query.whereclause.right.value, uuid.UUID) and query.whereclause.right.value == recipe_id:
            return mock_recipe_result
        # If it's querying for ingredient
        elif isinstance(query.whereclause.right.value, uuid.UUID) and query.whereclause.right.value == ingredient_id:
            return mock_ingredient_result
        return None
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    # Execute
    result = await recipe_repository.find_by_id(recipe_id)
    
    # Assert
    assert result is not None
    assert result.id == recipe_id
    assert result.name == "Test Recipe"
    assert len(result.ingredients) == 1
    assert result.ingredients[0].ingredient_id == ingredient_id
    assert result.ingredients[0].name == "Test Ingredient"
    assert mock_session.execute.call_count >= 1


@pytest.mark.asyncio
async def test_find_by_id_not_found(recipe_repository, mock_session, recipe_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await recipe_repository.find_by_id(recipe_id)
    
    # Assert
    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_name(recipe_repository, mock_session, recipe_model, recipe_ingredient_model, ingredient_model):
    # Setup
    recipe_model.ingredients = [recipe_ingredient_model]
    
    mock_recipe_result = MagicMock()
    mock_recipe_result.scalars.return_value.first.return_value = recipe_model
    
    mock_ingredient_result = MagicMock()
    mock_ingredient_result.scalars.return_value.first.return_value = ingredient_model
    
    mock_session.execute.side_effect = [mock_recipe_result, mock_ingredient_result]
    
    # Execute
    result = await recipe_repository.find_by_name("Test Recipe")
    
    # Assert
    assert result is not None
    assert result.name == "Test Recipe"
    assert mock_session.execute.call_count >= 1


@pytest.mark.asyncio
async def test_find_all(recipe_repository, mock_session, recipe_model, recipe_ingredient_model, ingredient_model):
    # Setup
    recipe_model.ingredients = [recipe_ingredient_model]
    
    mock_recipes_result = MagicMock()
    mock_recipes_result.scalars.return_value.all.return_value = [recipe_model]
    
    mock_ingredient_result = MagicMock()
    mock_ingredient_result.scalars.return_value.first.return_value = ingredient_model
    
    mock_session.execute.side_effect = [mock_recipes_result, mock_ingredient_result]
    
    # Execute
    result = await recipe_repository.find_all(skip=0, limit=10)
    
    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0].name == "Test Recipe"
    assert mock_session.execute.call_count >= 1


@pytest.mark.asyncio
async def test_search(recipe_repository, mock_session, recipe_model, recipe_ingredient_model, ingredient_model):
    # Setup
    recipe_model.ingredients = [recipe_ingredient_model]
    
    mock_recipes_result = MagicMock()
    mock_recipes_result.scalars.return_value.all.return_value = [recipe_model]
    
    mock_ingredient_result = MagicMock()
    mock_ingredient_result.scalars.return_value.first.return_value = ingredient_model
    
    mock_session.execute.side_effect = [mock_recipes_result, mock_ingredient_result]
    
    # Execute
    result = await recipe_repository.search("Test")
    
    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0].name == "Test Recipe"
    assert mock_session.execute.call_count >= 1


@pytest.mark.asyncio
async def test_find_by_ingredient(recipe_repository, mock_session, recipe_model, recipe_ingredient_model, ingredient_id, ingredient_model):
    # Setup
    recipe_model.ingredients = [recipe_ingredient_model]
    
    mock_recipes_result = MagicMock()
    mock_recipes_result.scalars.return_value.all.return_value = [recipe_model]
    
    mock_ingredient_result = MagicMock()
    mock_ingredient_result.scalars.return_value.first.return_value = ingredient_model
    
    mock_session.execute.side_effect = [mock_recipes_result, mock_ingredient_result]
    
    # Execute
    result = await recipe_repository.find_by_ingredient(ingredient_id)
    
    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0].name == "Test Recipe"
    assert mock_session.execute.call_count >= 1


@pytest.mark.asyncio
async def test_update(recipe_repository, mock_session, recipe, recipe_model, recipe_ingredient_model, recipe_id):
    # Setup
    recipe_model.ingredients = [recipe_ingredient_model]
    
    mock_recipe_result = MagicMock()
    mock_recipe_result.scalars.return_value.first.return_value = recipe_model
    
    mock_ingredients_result = MagicMock()
    mock_ingredients_result.scalars.return_value.all.return_value = [recipe_ingredient_model]
    
    mock_ingredient_result = MagicMock()
    mock_ingredient_result.scalars.return_value.first.return_value = None
    
    # Configure multiple return values for session.execute
    mock_session.execute.side_effect = [mock_recipe_result, mock_ingredients_result]
    
    # Execute
    result = await recipe_repository.update(recipe)
    
    # Assert
    assert result == recipe
    assert mock_session.execute.call_count >= 1
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(recipe_repository, mock_session, recipe, recipe_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute and Assert
    with pytest.raises(ValueError):
        await recipe_repository.update(recipe)
    
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete(recipe_repository, mock_session, recipe_model, recipe_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = recipe_model
    mock_session.execute.return_value = mock_result
    
    # Execute
    await recipe_repository.delete(recipe_id)
    
    # Assert
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(recipe_repository, mock_session, recipe_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute
    await recipe_repository.delete(recipe_id)
    
    # Assert
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()