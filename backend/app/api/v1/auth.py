"""
Authentication API endpoints for Engineering Intelligence Hub.

Provides user registration, login, and profile management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from dependencies import get_db, get_current_active_user
from services.auth_service import AuthService
from schemas.user import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    TokenResponse, 
    AuthResponse,
    UserUpdate,
    UserPasswordUpdate
)
from models.user import User
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user account.
    
    Args:
        user_create: User registration data
        db: Database session
        
    Returns:
        AuthResponse: Authentication response with token and user data
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        auth_service = AuthService()
        
        # Register user
        user = await auth_service.register_user(db, user_create)
        
        # Create login credentials for immediate login after registration
        user_login = UserLogin(email=user_create.email, password=user_create.password)
        
        # Login user to get token
        token_response = await auth_service.login_user(db, user_login)
        
        # Create success response
        response = AuthResponse(
            success=True,
            message="User registered successfully",
            data=token_response
        )
        
        logger.info(f"User registered and logged in: {user.email}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Login user with email and password.
    
    Args:
        user_login: Login credentials
        db: Database session
        
    Returns:
        AuthResponse: Authentication response with token and user data
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        auth_service = AuthService()
        
        # Login user
        token_response = await auth_service.login_user(db, user_login)
        
        # Create success response
        response = AuthResponse(
            success=True,
            message="Login successful", 
            data=token_response
        )
        
        logger.info(f"User logged in: {user_login.email}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Logout current user.
    
    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by removing the token. This endpoint serves as a confirmation and for logging.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Logout confirmation message
    """
    logger.info(f"User logged out: {current_user.email}")
    return {
        "success": True,
        "message": "Logout successful",
        "detail": "Token should be removed from client storage"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user profile information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user data
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update current user profile.
    
    Args:
        user_update: Profile update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Updated user data
        
    Raises:
        HTTPException: If validation fails or email already exists
    """
    try:
        auth_service = AuthService()
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        if user_update.full_name is not None:
            update_data["full_name"] = user_update.full_name
        if user_update.email is not None:
            update_data["email"] = user_update.email
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update user profile
        updated_user = await auth_service.update_user_profile(
            db, current_user.id, update_data
        )
        
        logger.info(f"User profile updated: {updated_user.email}")
        return UserResponse.model_validate(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password")
async def change_password(
    password_update: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Change user password.
    
    Args:
        password_update: Password change data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Success confirmation
        
    Raises:
        HTTPException: If current password is incorrect or validation fails
    """
    try:
        auth_service = AuthService()
        
        # Change password
        await auth_service.change_password(
            db,
            current_user.id,
            password_update.current_password,
            password_update.new_password
        )
        
        logger.info(f"Password changed for user: {current_user.email}")
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/deactivate")
async def deactivate_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Deactivate current user account.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Deactivation confirmation
    """
    try:
        auth_service = AuthService()
        
        # Deactivate user
        success = await auth_service.deactivate_user(db, current_user.id)
        
        if success:
            logger.info(f"User account deactivated: {current_user.email}")
            return {
                "success": True,
                "message": "Account deactivated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account deactivation failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account deactivation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deactivation failed"
        )


# Health check for auth service
@router.get("/health")
async def auth_health_check() -> Any:
    """
    Health check for authentication service.
    
    Returns:
        dict: Health status
    """
    return {
        "service": "authentication",
        "status": "healthy",
        "endpoints": [
            "/auth/register",
            "/auth/login", 
            "/auth/logout",
            "/auth/me",
            "/auth/change-password",
            "/auth/deactivate"
        ]
    }