```
inventory_service/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── ingredient.py
│   │   │   └── recipe.py
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── quantity.py
│   │   │   └── unit_of_measure.py
│   │   ├── aggregates/
│   │   │   ├── __init__.py
│   │   │   └── ingredient_aggregate.py
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   └── domain_exceptions.py
│   │   ├── ports/
│   │   │   ├── __init__.py
│   │   │   ├── input/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── inventory_service_port.py
│   │   │   │   └── inventory_query_port.py
│   │   │   └── output/
│   │   │       ├── __init__.py
│   │   │       ├── ingredient_repository_port.py
│   │   │       ├── recipe_repository_port.py
│   │   │       └── event_publisher_port.py
│   │   └── __init__.py
│   ├── application/
│   │   ├── dtos/
│   │   │   ├── __init__.py
│   │   │   ├── ingredient_dto.py
│   │   │   └── recipe_dto.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── inventory_service.py
│   │   │   └── inventory_query_service.py
│   │   ├── mappers/
│   │   │   ├── __init__.py
│   │   │   ├── ingredient_mapper.py
│   │   │   └── recipe_mapper.py
│   │   ├── events/
│   │   │   ├── __init__.py
│   │   │   └── inventory_events.py
│   │   └── __init__.py
│   ├── infrastructure/
│   │   ├── adapters/
│   │   │   ├── __init__.py
│   │   │   ├── input/
│   │   │   │   ├── __init__.py
│   │   │   │   └── api/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── inventory_controller.py
│   │   │   │       ├── inventory_router.py
│   │   │   │       ├── schemas.py
│   │   │   │       └── error_handler.py
│   │   │   └── output/
│   │   │       ├── __init__.py
│   │   │       ├── repositories/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── ingredient_repository.py
│   │   │       │   └── recipe_repository.py
│   │   │       └── messaging/
│   │   │           ├── __init__.py
│   │   │           └── kafka_event_publisher.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ingredient_model.py
│   │   │   │   └── recipe_model.py
│   │   │   ├── migrations/
│   │   │   │   ├── versions/
│   │   │   │   ├── env.py
│   │   │   │   ├── README
│   │   │   │   ├── script.py.mako
│   │   │   │   └── alembic.ini
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   └── test_ingredient_aggregate.py
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   └── test_inventory_service.py
│   │   └── __init__.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_inventory_api.py
│   └── __init__.py
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── .env.example
├── main.py
└── README.md

```