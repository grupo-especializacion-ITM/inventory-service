from functools import lru_cache
from typing import Optional, Dict, Any

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Restaurant Inventory Service"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "API for managing restaurant inventory"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str = 'postgresql://adrielmachado0111:Afwl6cC7hKUN@ep-aged-band-882777-pooler.us-east-2.aws.neon.tech/inventory_service'
    DB_ECHO: bool = False
    
    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_INVENTORY_TOPIC: str = "restaurant.inventory"
    KAFKA_CLIENT_ID: str = "inventory-service"
    KAFKA_GROUP_ID: str = "inventory-service-group"
    
    # API settings
    API_PREFIX: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: str = "*"
    
    @field_validator("CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str) -> list:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()