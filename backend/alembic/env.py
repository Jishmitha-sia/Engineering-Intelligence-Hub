"""
Alembic environment configuration for Engineering Intelligence Hub.

Handles database migrations with async SQLAlchemy support.
"""

import asyncio
import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Add app directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "app"))

# Import app configuration and models
from config import settings
from db.base import Base, import_all_models

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Alembic can detect them
import_all_models()

# Set target metadata for autogenerate support
target_metadata = Base.metadata

# Override sqlalchemy.url with app configuration
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter objects to include in migrations.
    
    Args:
        object: The object being considered
        name: Name of the object
        type_: Type of object (table, column, etc.)
        reflected: Whether object was reflected from database
        compare_to: Object being compared to
        
    Returns:
        bool: Whether to include object in migration
    """
    # Skip Alembic version table
    if type_ == "table" and name == "alembic_version":
        return False
    
    # Skip temporary tables
    if type_ == "table" and name.startswith("temp_"):
        return False
    
    # Include everything else
    return True


def include_name(name, type_, parent_names):
    """
    Filter names to include in migrations.
    
    Args:
        name: Name being considered
        type_: Type of object
        parent_names: Names of parent objects
        
    Returns:
        bool: Whether to include name
    """
    # Skip system schemas
    if type_ == "schema" and name in ["information_schema", "pg_catalog"]:
        return False
    
    return True


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        include_name=include_name,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with database connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        include_name=include_name,
        compare_type=True,
        compare_server_default=True,
        # Render as batch for SQLite compatibility (though we use PostgreSQL)
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """
    Run migrations in 'online' mode with async engine.
    
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Create async engine
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,  # Don't use connection pooling for migrations
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


# Determine migration mode and run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()