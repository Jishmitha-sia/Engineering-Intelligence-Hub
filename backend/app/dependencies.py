"""
FastAPI Dependencies for Engineering Intelligence Hub.

Provides dependency injection for database sessions, authentication, and other services.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from models.user import User
from models.workspace import WorkspaceMember


# Security scheme for JWT tokens
security = HTTPBearer()


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session.
    
    Yields:
        AsyncSession: Database session
    """
    from db.session import get_async_session
    async for session in get_async_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency for getting current authenticated user.
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    from services.auth_service import AuthService
    
    auth_service = AuthService()
    return await auth_service.get_current_user(db, credentials.credentials)


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Dependency for getting current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    # db: AsyncSession = Depends(get_db)  # Uncomment after Task 1.2
):
    """
    Dependency for getting current user (optional).
    
    Returns None if no valid token provided, useful for endpoints that
    work with or without authentication.
    
    Args:
        credentials: Optional JWT token
        db: Database session
        
    Returns:
        Optional[User]: Current user or None
    """
    # TODO: Implement in Task 1.3 after auth setup
    # if not credentials:
    #     return None
    
    # try:
    #     return await get_current_user(credentials, db)
    # except HTTPException:
    #     return None
    pass


def require_workspace_access(workspace_id: int):
    """
    Dependency factory for workspace access control.
    """
    async def _check_access(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> WorkspaceMember:
        from services.workspace_service import WorkspaceService

        service = WorkspaceService()
        return await service.require_membership(db, workspace_id, current_user.id)

    return _check_access


def require_workspace_owner(workspace_id: int):
    """
    Dependency factory for workspace owner access control.
    """
    async def _check_owner(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> WorkspaceMember:
        from models.workspace import WorkspaceRole
        from services.workspace_service import WorkspaceService

        service = WorkspaceService()
        return await service.require_membership(
            db,
            workspace_id,
            current_user.id,
            required_role=WorkspaceRole.OWNER,
        )

    return _check_owner


# Rate limiting dependencies (will be implemented in Phase 9)
def rate_limit_authenticated():
    """Rate limiting for authenticated users."""
    # TODO: Implement in Phase 9
    pass


def rate_limit_unauthenticated():
    """Rate limiting for unauthenticated users.""" 
    # TODO: Implement in Phase 9
    pass