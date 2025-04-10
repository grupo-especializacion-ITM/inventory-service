import json
import logging
from typing import Any, Dict, Optional
from aiokafka import AIOKafkaProducer
import asyncio

from src.domain.ports.output.event_publisher_port import EventPublisherPort
from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe
from src.application.events.inventory_events import (
    IngredientCreatedEvent,
    IngredientUpdatedEvent,
    IngredientStockChangedEvent,
    LowStockAlertEvent,
    RecipeCreatedEvent,
    RecipeUpdatedEvent
)
from src.infrastructure.config.settings import get_settings


logger = logging.getLogger(__name__)


class KafkaEventPublisher(EventPublisherPort):
    def __init__(self):
        self.settings = get_settings()
        self.producer = None
        self.default_topic = self.settings.KAFKA_INVENTORY_TOPIC
    
    async def start(self):
        """Start the Kafka producer"""
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=self.settings.KAFKA_CLIENT_ID,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None
            )
            
            await self.producer.start()
            logger.info("Kafka producer started")
    
    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer is not None:
            await self.producer.stop()
            self.producer = None
            logger.info("Kafka producer stopped")
    
    async def publish_ingredient_created(self, ingredient: Ingredient) -> None:
        """Publish an ingredient created event"""
        # Create event
        event = IngredientCreatedEvent.create(
            ingredient_id=ingredient.id,
            name=ingredient.name,
            quantity=ingredient.quantity.value,
            unit_of_measure=ingredient.unit_of_measure.unit,
            category=ingredient.category
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(ingredient.id)
        )
    
    async def publish_ingredient_updated(self, ingredient: Ingredient) -> None:
        """Publish an ingredient updated event"""
        # Create event
        event = IngredientUpdatedEvent.create(
            ingredient_id=ingredient.id,
            name=ingredient.name,
            quantity=ingredient.quantity.value,
            unit_of_measure=ingredient.unit_of_measure.unit,
            category=ingredient.category
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(ingredient.id)
        )
    
    async def publish_ingredient_stock_changed(
        self, 
        ingredient: Ingredient, 
        previous_quantity: float,
        change_type: str
    ) -> None:
        """Publish an ingredient stock changed event"""
        # Create event
        event = IngredientStockChangedEvent.create(
            ingredient_id=ingredient.id,
            name=ingredient.name,
            previous_quantity=previous_quantity,
            new_quantity=ingredient.quantity.value,
            unit_of_measure=ingredient.unit_of_measure.unit,
            change_type=change_type
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(ingredient.id)
        )
    
    async def publish_low_stock_alert(self, ingredient: Ingredient) -> None:
        """Publish a low stock alert event"""
        # Create event
        event = LowStockAlertEvent.create(
            ingredient_id=ingredient.id,
            name=ingredient.name,
            current_quantity=ingredient.quantity.value,
            minimum_stock=ingredient.minimum_stock.value,
            unit_of_measure=ingredient.unit_of_measure.unit
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(ingredient.id)
        )
    
    async def publish_recipe_created(self, recipe: Recipe) -> None:
        """Publish a recipe created event"""
        # Prepare ingredient data for the event
        ingredients_data = [
            {
                "ingredient_id": str(ing.ingredient_id),
                "name": ing.name,
                "quantity": ing.quantity,
                "unit_of_measure": ing.unit_of_measure
            }
            for ing in recipe.ingredients
        ]
        
        # Create event
        event = RecipeCreatedEvent.create(
            recipe_id=recipe.id,
            name=recipe.name,
            ingredients=ingredients_data
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(recipe.id)
        )
    
    async def publish_recipe_updated(self, recipe: Recipe) -> None:
        """Publish a recipe updated event"""
        # Prepare ingredient data for the event
        ingredients_data = [
            {
                "ingredient_id": str(ing.ingredient_id),
                "name": ing.name,
                "quantity": ing.quantity,
                "unit_of_measure": ing.unit_of_measure
            }
            for ing in recipe.ingredients
        ]
        
        # Create event
        event = RecipeUpdatedEvent.create(
            recipe_id=recipe.id,
            name=recipe.name,
            ingredients=ingredients_data
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(recipe.id)
        )
    
    async def publish_event(self, event_type: str, payload: Dict[str, Any], topic: Optional[str] = None, key: Optional[str] = None) -> None:
        """Publish a generic event to Kafka"""
        if self.producer is None:
            await self.start()
        
        try:
            # Use the provided topic or default to the configured topic
            kafka_topic = topic or self.default_topic
            
            # Publish the message
            await self.producer.send_and_wait(
                topic=kafka_topic,
                value=payload,
                key=key
            )
            
            logger.info(f"Event {event_type} published to topic {kafka_topic}")
            
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {str(e)}")
            # In a production system, we might want to implement a retry mechanism,
            # or store failed events for later reprocessing
            raise