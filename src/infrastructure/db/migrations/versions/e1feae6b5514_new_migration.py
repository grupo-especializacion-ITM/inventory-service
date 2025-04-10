"""new_migration

Revision ID: e1feae6b5514
Revises: 
Create Date: 2025-04-08 22:15:35.207330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e1feae6b5514'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE SCHEMA IF NOT EXISTS inventory_service")
    op.create_table(
        'ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v1()")),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit_of_measure', sa.String(50), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('minimum_stock', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        schema='inventory_service'
    )
    
    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v1()")),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('preparation_time', sa.Integer(), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        schema='inventory_service'
    )
    
    # Create recipe_ingredients table (many-to-many relationship)
    op.create_table(
        'recipe_ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v1()")),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ingredient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit_of_measure', sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(['recipe_id'], ['inventory_service.recipes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ingredient_id'], ['inventory_service.ingredients.id'], ondelete='CASCADE'),
        schema='inventory_service'
    )
    
    # Create indexes
    op.create_index('ix_ingredients_name', 'ingredients', ['name'], unique=True, schema='inventory_service')
    op.create_index('ix_ingredients_category', 'ingredients', ['category'], schema='inventory_service')
    op.create_index('ix_recipes_name', 'recipes', ['name'], unique=True, schema='inventory_service')
    op.create_index('ix_recipe_ingredients_ingredient_id', 'recipe_ingredients', ['ingredient_id'], schema='inventory_service')


def downgrade() -> None:
    op.drop_table('recipe_ingredients', schema='inventory_service')
    op.drop_table('recipes', schema='inventory_service')
    op.drop_table('ingredients', schema='inventory_service')
    op.execute("DROP SCHEMA inventory_service CASCADE")
