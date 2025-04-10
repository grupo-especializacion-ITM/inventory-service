from typing import List, Optional
from uuid import UUID

from src.domain.entities.ingredient import Ingredient
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.unit_of_measure import UnitOfMeasure
from src.application.dtos.ingredient_dto import IngredientDTO


class IngredientMapper:
    @staticmethod
    def to_entity(dto: IngredientDTO) -> Ingredient:
        """
        Map IngredientDTO to Ingredient entity
        """
        return Ingredient(
            id=dto.id if dto.id else UUID(),
            name=dto.name,
            quantity=Quantity(dto.quantity),
            unit_of_measure=UnitOfMeasure(dto.unit_of_measure),
            category=dto.category,
            minimum_stock=Quantity(dto.minimum_stock),
            created_at=dto.created_at if dto.created_at else None,
            updated_at=dto.updated_at
        )
    
    @staticmethod
    def to_dto(entity: Ingredient) -> IngredientDTO:
        """
        Map Ingredient entity to IngredientDTO
        """
        return IngredientDTO(
            id=entity.id,
            name=entity.name,
            quantity=entity.quantity.value,
            unit_of_measure=entity.unit_of_measure.unit,
            category=entity.category,
            minimum_stock=entity.minimum_stock.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def to_dto_list(entities: List[Ingredient]) -> List[IngredientDTO]:
        """
        Map a list of Ingredient entities to a list of IngredientDTOs
        """
        return [IngredientMapper.to_dto(entity) for entity in entities]