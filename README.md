# Microservicio de Inventario para Restaurantes

Este proyecto implementa un microservicio para la gestión de inventario en un sistema de restaurantes, utilizando arquitectura hexagonal (puertos y adaptadores).

## Tecnologías utilizadas

- Python 3.13+
- FastAPI: Framework web de alto rendimiento
- SQLAlchemy: ORM para la interacción con la base de datos
- Alembic: Herramienta para migraciones de base de datos
- Kafka: Comunicación asíncrona entre microservicios
- PostgreSQL: Base de datos relacional

## Arquitectura Hexagonal

El proyecto sigue los principios de la arquitectura hexagonal (puertos y adaptadores):

### Capa de Dominio 

Contiene:
- Entidades (Ingredient, Recipe)
- Objetos de valor (Quantity, UnitOfMeasure)
- Agregados (IngredientAggregate, RecipeWithIngredientsAggregate)
- Puertos de entrada/salida para definir las interfaces

### Capa de Aplicación

Contiene:
- Servicios que implementan los puertos de entrada
- DTOs para la comunicación entre capas
- Eventos de dominio

### Capa de Infraestructura

Contiene:
- Adaptadores de entrada (API REST con FastAPI)
- Adaptadores de salida (Repositorio SQL, Publisher de Kafka)
- Configuración de la aplicación

## Estructura del proyecto

```
inventory_service/
├── src/
│   ├── domain/             # Capa de dominio
│   │   ├── entities/       # Entidades del dominio
│   │   ├── value_objects/  # Objetos de valor
│   │   ├── aggregates/     # Agregados
│   │   ├── exceptions/     # Excepciones del dominio
│   │   └── ports/          # Puertos (entrada/salida)
│   ├── application/        # Capa de aplicación
│   │   ├── dtos/           # Objetos de transferencia de datos
│   │   ├── services/       # Servicios de aplicación
│   │   ├── mappers/        # Mapeadores entre entidades y DTOs
│   │   └── events/         # Eventos de dominio
│   └── infrastructure/     # Capa de infraestructura
│       ├── adapters/       # Adaptadores (entrada/salida)
│       ├── db/             # Configuración de base de datos y migraciones
│       └── config/         # Configuraciones
├── tests/                  # Pruebas unitarias e integración
├── alembic.ini             # Configuración de Alembic
└── main.py                 # Punto de entrada de la aplicación
```

## Configuración del entorno

1. Crear un archivo `.env` en la raíz del proyecto con la siguiente configuración:

```
INVENTORY_DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/inventory_db
DB_ECHO=True
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
DEBUG=True
```

## Migraciones de base de datos

Para ejecutar las migraciones de base de datos:

```bash
# Crear una nueva migración
alembic revision --autogenerate -m "descripción_de_la_migración"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

## Ejecución de la aplicación

### Modo desarrollo

```bash
uvicorn main:app --reload
```

### Con Docker

```bash
docker build -t inventory-service .
docker run -p 8001:8001 --env-file .env inventory-service
```

## API Endpoints

### Ingredientes

- `POST /api/v1/ingredients`: Crear un nuevo ingrediente
- `GET /api/v1/ingredients/{ingredient_id}`: Obtener un ingrediente por ID
- `PATCH /api/v1/ingredients/{ingredient_id}`: Actualizar un ingrediente
- `PUT /api/v1/ingredients/{ingredient_id}/stock`: Actualizar el stock de un ingrediente
- `POST /api/v1/ingredients/{ingredient_id}/stock/add`: Añadir stock a un ingrediente
- `POST /api/v1/ingredients/{ingredient_id}/stock/remove`: Reducir stock de un ingrediente
- `GET /api/v1/ingredients`: Obtener todos los ingredientes con paginación
- `GET /api/v1/ingredients/search?query={query}`: Buscar ingredientes por nombre
- `GET /api/v1/ingredients/category/{category}`: Obtener ingredientes por categoría
- `GET /api/v1/ingredients/low-stock`: Obtener ingredientes por debajo del stock mínimo

### Recetas

- `POST /api/v1/recipes`: Crear una nueva receta
- `GET /api/v1/recipes/{recipe_id}`: Obtener una receta por ID
- `PATCH /api/v1/recipes/{recipe_id}`: Actualizar una receta
- `GET /api/v1/recipes`: Obtener todas las recetas con paginación
- `GET /api/v1/recipes/search?query={query}`: Buscar recetas por nombre
- `GET /api/v1/recipes/by-ingredient/{ingredient_id}`: Obtener recetas que utilizan un ingrediente específico
- `GET /api/v1/recipes/{recipe_id}/availability?quantity={quantity}`: Verificar disponibilidad de ingredientes para una receta

### Validación de Inventario

- `POST /api/v1/inventory/validate`: Validar disponibilidad de productos

## Eventos

El servicio publica los siguientes eventos en Kafka:

- `inventory.ingredient.created`: Cuando se crea un nuevo ingrediente
- `inventory.ingredient.updated`: Cuando se actualiza un ingrediente
- `inventory.ingredient.stock_changed`: Cuando cambia el stock de un ingrediente
- `inventory.ingredient.low_stock`: Cuando un ingrediente cae por debajo del stock mínimo
- `inventory.recipe.created`: Cuando se crea una nueva receta
- `inventory.recipe.updated`: Cuando se actualiza una receta
- `inventory.validation.performed`: Cuando se realiza una validación de disponibilidad