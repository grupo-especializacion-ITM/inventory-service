from typing import List, Optional, Dict, Any
from uuid import UUID

from src.domain.entities.recipe import Recipe, RecipeIngredient
from src.application.dtos.recipe_dto import RecipeDTO, RecipeIngredientDTO


class RecipeMapper:
    @staticmethod
    def to_entity(dto: RecipeDTO) -> Recipe:
        """
        Map RecipeDTO to Recipe entity
        """
        ingredients = []
        for ingredient_dto in dto.ingredients:
            ingredient = RecipeIngredient(
                ingredient_id=ingredient_dto.ingredient_id,
                name=ingredient_dto.name,
                quantity=ingredient_dto.quantity,
                unit_of_measure=ingredient_dto.unit_of_measure
            )
            ingredients.append(ingredient)
        
        return Recipe(
            id=dto.id if dto.id else UUID(),
            name=dto.name,
            ingredients=ingredients,
            preparation_time=dto.preparation_time,
            instructions=dto.instructions,
            created_at=dto.created_at if dto.created_at else None,
            updated_at=dto.updated_at
        )
    
    @staticmethod
    def to_dto(entity: Recipe) -> RecipeDTO:
        """
        Map Recipe entity to RecipeDTO
        """
        ingredients = []
        for ingredient_entity in entity.ingredients:
            ingredient_dto = RecipeIngredientDTO(
                ingredient_id=ingredient_entity.ingredient_id,
                name=ingredient_entity.name,
                quantity=ingredient_entity.quantity,
                unit_of_measure=ingredient_entity.unit_of_measure
            )
            ingredients.append(ingredient_dto)
        
        return RecipeDTO(
            id=entity.id,
            name=entity.name,
            ingredients=ingredients,
            preparation_time=entity.preparation_time,
            instructions=entity.instructions,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def to_dto_list(entities: List[Recipe]) -> List[RecipeDTO]:
        """
        Map a list of Recipe entities to a list of RecipeDTOs
        """
        return [RecipeMapper.to_dto(entity) for entity in entities]