"""
Database session management for Engineering Intelligence Hub.

Provides async SQLAlchemy engine and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import asyncio
from typing import AsyncGenerator
import logging

from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create async engine
_engine_kwargs: dict = {
    "echo": settings.DEBUG,
    "future": True,
}

if settings.ENVIRONMENT == "testing":
    _engine_kwargs["poolclass"] = NullPool
else:
    _engine_kwargs.update(
        {
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
            "pool_recycle": settings.DATABASE_POOL_RECYCLE,
        }
    )

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Alternative session dependency (alias for get_async_session).
    
    Yields:
        AsyncSession: Database session
    """
    async for session in get_async_session():
        yield session


# Connection and health check functions
async def check_database_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def create_database_if_not_exists():
    """
    Create database if it doesn't exist.
    
    Note: This is mainly for development/testing environments.
    In production, database should be created externally.
    """
    if settings.ENVIRONMENT == "production":
        logger.warning("Skipping database creation in production")
        return
    
    try:
        # Extract database name from URL
        import urllib.parse
        parsed = urllib.parse.urlparse(settings.DATABASE_URL)
        database_name = parsed.path[1:]  # Remove leading slash
        
        # Create connection to postgres database (without specific db)
        postgres_url = settings.DATABASE_URL.replace(f"/{database_name}", "/postgres")
        temp_engine = create_async_engine(postgres_url, poolclass=NullPool)
        
        async with temp_engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
            )
            exists = result.fetchone()
            
            if not exists:
                # Create database
                await conn.execute(text(f"CREATE DATABASE {database_name}"))
                logger.info(f"Created database: {database_name}")
            else:
                logger.info(f"Database already exists: {database_name}")
        
        await temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise


async def ensure_pgvector_extension():
    """
    Ensure pgvector extension is installed and enabled.
    
    This is required for vector similarity search functionality.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Check if pgvector extension exists
            result = await session.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            exists = result.fetchone()
            
            if not exists:
                # Create pgvector extension
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await session.commit()
                logger.info("pgvector extension created")
            else:
                logger.info("pgvector extension already exists")
                
    except Exception as e:
        logger.error(f"Failed to ensure pgvector extension: {e}")
        raise


async def init_database():
    """
    Initialize database with required extensions and checks.

    Should be called during application startup.
    """
    logger.info("Initializing database...")

    # Database is provisioned by Docker Compose / external ops in normal dev/prod.
    # Auto-create is only useful for bare-metal local setup without a DB container.
    if settings.ENVIRONMENT == "testing":
        await create_database_if_not_exists()

    if not await check_database_connection():
        raise RuntimeError("Could not connect to database")

    await ensure_pgvector_extension()

    logger.info("Database initialization complete")


async def close_database_connections():
    """
    Close all database connections.
    
    Should be called during application shutdown.
    """
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Database connections closed")


# Context manager for manual session handling
class DatabaseSession:
    """Context manager for manual database session handling."""
    
    def __init__(self):
        self.session: AsyncSession = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()


# Utility functions for testing
async def create_test_database():
    """Create test database. Only for testing."""
    if settings.ENVIRONMENT != "testing":
        raise RuntimeError("Test database creation only allowed in testing environment")
    
    await create_database_if_not_exists()
    await ensure_pgvector_extension()


async def drop_test_database():
    """Drop test database. Only for testing."""
    if settings.ENVIRONMENT != "testing":
        raise RuntimeError("Test database deletion only allowed in testing environment")
    
    try:
        import urllib.parse
        parsed = urllib.parse.urlparse(settings.DATABASE_URL)
        database_name = parsed.path[1:]
        
        postgres_url = settings.DATABASE_URL.replace(f"/{database_name}", "/postgres")
        temp_engine = create_async_engine(postgres_url, poolclass=NullPool)
        
        async with temp_engine.begin() as conn:
            # Terminate active connections
            await conn.execute(text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{database_name}'
                AND pid <> pg_backend_pid()
            """))
            
            # Drop database
            await conn.execute(text(f"DROP DATABASE IF EXISTS {database_name}"))
        
        await temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"Failed to drop test database: {e}")
        raise