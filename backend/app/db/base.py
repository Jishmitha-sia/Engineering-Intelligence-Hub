"""
Database base models and metadata for Engineering Intelligence Hub.

Provides SQLAlchemy base class and metadata configuration.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from typing import Any

# Naming convention for constraints
# This ensures consistent naming across different database systems
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Modern SQLAlchemy 2.0 declarative base
class Base(DeclarativeBase):
    """
    Base class for all database models.
    
    Uses SQLAlchemy 2.0 declarative syntax with type annotations.
    """
    metadata = metadata
    
    # Common attributes that might be useful across models
    __abstract__ = True


# Legacy support for older SQLAlchemy patterns (if needed)
# Base = declarative_base(metadata=metadata)


# Import all model modules here to ensure they are registered with SQLAlchemy
# This is important for Alembic to detect model changes
def import_all_models():
    """
    Import all model modules to register them with SQLAlchemy.
    
    This function should be called before running Alembic migrations
    to ensure all models are properly detected.
    """
    from models import user  # noqa: F401


# Table prefixes for organization (optional)
TABLE_PREFIX = ""

def get_table_name(model_name: str) -> str:
    """
    Generate standardized table name.
    
    Args:
        model_name: Name of the model (e.g., "User", "Workspace")
        
    Returns:
        str: Formatted table name (e.g., "users", "workspaces")
    """
    # Convert CamelCase to snake_case and pluralize
    import re
    
    # Convert CamelCase to snake_case
    snake_case = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', model_name)
    snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_case).lower()
    
    # Add table prefix if configured
    if TABLE_PREFIX:
        snake_case = f"{TABLE_PREFIX}_{snake_case}"
    
    # Simple pluralization (add 's', handle 'y' endings)
    if snake_case.endswith('y') and len(snake_case) > 1:
        plural = snake_case[:-1] + 'ies'
    elif snake_case.endswith(('s', 'x', 'z', 'ch', 'sh')):
        plural = snake_case + 'es'
    else:
        plural = snake_case + 's'
    
    return plural


# Common column types and mixins that can be reused
from sqlalchemy import Column, Integer, DateTime, Boolean, String, Text
from sqlalchemy.sql import func
from datetime import datetime


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when record was last updated"
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when record was soft deleted"
    )
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether record is soft deleted"
    )


class ActiveMixin:
    """Mixin for active/inactive status."""
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether record is active"
    )


# Database utilities
async def create_all_tables():
    """
    Create all database tables.
    
    Note: In production, use Alembic migrations instead.
    This is mainly for development and testing.
    """
    from db.session import engine
    
    # Import all models first
    import_all_models()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables():
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    Only use in development/testing.
    """
    from db.session import engine
    from config import settings
    
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot drop tables in production environment")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)