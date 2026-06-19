"""
Authentication service for Engineering Intelligence Hub.

Provides user registration, login, and authentication logic.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
import logging

from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from core.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    verify_token,
    is_valid_password
)
from config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication operations."""
    
    async def register_user(
        self, 
        db: AsyncSession, 
        user_create: UserCreate
    ) -> User:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_create: User registration data
            
        Returns:
            User: Created user instance
            
        Raises:
            HTTPException: If email already exists or validation fails
        """
        # Check if user with email already exists
        existing_user = await self.get_user_by_email(db, user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        is_valid, errors = is_valid_password(user_create.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(errors)}"
            )
        
        # Create user instance
        db_user = User(
            email=user_create.email.lower(),  # Store email in lowercase
            full_name=user_create.full_name,
            hashed_password=hash_password(user_create.password),
            is_active=True,
            is_verified=False,  # Email verification required
        )
        
        # Add to database
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"New user registered: {db_user.email} (ID: {db_user.id})")
        return db_user
    
    async def authenticate_user(
        self, 
        db: AsyncSession, 
        user_login: UserLogin
    ) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            user_login: Login credentials
            
        Returns:
            Optional[User]: Authenticated user or None if invalid
        """
        # Get user by email
        user = await self.get_user_by_email(db, user_login.email)
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {user_login.email}")
            return None
        
        # Verify password
        if not verify_password(user_login.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {user_login.email}")
            return None
        
        # Update last login timestamp
        await self.update_last_login(db, user.id)
        
        logger.info(f"Successful login: {user.email} (ID: {user.id})")
        return user
    
    async def login_user(
        self, 
        db: AsyncSession, 
        user_login: UserLogin
    ) -> TokenResponse:
        """
        Login user and create access token.
        
        Args:
            db: Database session
            user_login: Login credentials
            
        Returns:
            TokenResponse: Authentication token and user data
            
        Raises:
            HTTPException: If authentication fails
        """
        # Authenticate user
        user = await self.authenticate_user(db, user_login)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            subject=user.id, 
            expires_delta=access_token_expires
        )
        
        # Create response
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
        
        return token_response
    
    async def get_user_by_email(
        self, 
        db: AsyncSession, 
        email: str
    ) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            Optional[User]: User instance or None if not found
        """
        result = await db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Optional[User]: User instance or None if not found
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_current_user(
        self, 
        db: AsyncSession, 
        token: str
    ) -> User:
        """
        Get current user from JWT token.
        
        Args:
            db: Database session
            token: JWT access token
            
        Returns:
            User: Current authenticated user
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        # Verify token
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user ID
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await self.get_user_by_id(db, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is still active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    async def update_last_login(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            db: Database session
            user_id: User ID
        """
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.utcnow())
        )
        await db.commit()
    
    async def update_user_profile(
        self, 
        db: AsyncSession, 
        user_id: int, 
        update_data: dict
    ) -> User:
        """
        Update user profile information.
        
        Args:
            db: Database session
            user_id: User ID
            update_data: Fields to update
            
        Returns:
            User: Updated user instance
            
        Raises:
            HTTPException: If user not found or email already exists
        """
        # Get user
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if email is being updated and not already taken
        if "email" in update_data:
            new_email = update_data["email"].lower()
            if new_email != user.email:
                existing_user = await self.get_user_by_email(db, new_email)
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                update_data["email"] = new_email
                update_data["is_verified"] = False  # Re-verify email
        
        # Update user
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User profile updated: {user.email} (ID: {user.id})")
        return user
    
    async def change_password(
        self, 
        db: AsyncSession, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            db: Database session
            user_id: User ID
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            HTTPException: If current password is incorrect or validation fails
        """
        # Get user
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        is_valid, errors = is_valid_password(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(errors)}"
            )
        
        # Update password
        user.hashed_password = hash_password(new_password)
        await db.commit()
        
        logger.info(f"Password changed for user: {user.email} (ID: {user.id})")
        return True
    
    async def deactivate_user(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> bool:
        """
        Deactivate user account.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            bool: True if user deactivated successfully
        """
        result = await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await db.commit()
        
        if result.rowcount > 0:
            logger.info(f"User deactivated: ID {user_id}")
            return True
        
        return False