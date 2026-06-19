"""
User Pydantic schemas for Engineering Intelligence Hub.

Defines request/response schemas for user-related operations.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(
        ..., 
        description="User's email address",
        example="user@example.com"
    )
    full_name: Optional[str] = Field(
        None, 
        max_length=255,
        description="User's full name",
        example="John Doe"
    )


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="User's password (min 8 characters)",
        example="SecurePassword123"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(
        ..., 
        description="User's email address"
    )
    password: str = Field(
        ..., 
        description="User's password"
    )


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    
    full_name: Optional[str] = Field(
        None, 
        max_length=255,
        description="Updated full name"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Updated email address"
    )


class UserPasswordUpdate(BaseModel):
    """Schema for password updates."""
    
    current_password: str = Field(
        ...,
        description="Current password for verification"
    )
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="New password"
    )
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(UserBase):
    """Schema for user data in responses."""
    
    id: int = Field(
        ...,
        description="User's unique identifier"
    )
    is_active: bool = Field(
        ...,
        description="Whether user account is active"
    )
    is_verified: bool = Field(
        ...,
        description="Whether user's email is verified"
    )
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )
    last_login_at: Optional[datetime] = Field(
        None,
        description="Last login timestamp"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    expires_in: int = Field(
        ...,
        description="Token expiration time in seconds"
    )
    user: UserResponse = Field(
        ...,
        description="Authenticated user data"
    )


class AuthResponse(BaseModel):
    """Schema for authentication success response."""
    
    success: bool = Field(
        True,
        description="Whether authentication was successful"
    )
    message: str = Field(
        ...,
        description="Success message"
    )
    data: TokenResponse = Field(
        ...,
        description="Authentication data"
    )


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    
    users: list[UserResponse] = Field(
        ...,
        description="List of users"
    )
    total: int = Field(
        ...,
        description="Total number of users"
    )
    page: int = Field(
        ...,
        description="Current page number"
    )
    page_size: int = Field(
        ...,
        description="Number of users per page"
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages"
    )


# Utility schemas
class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""
    
    email: EmailStr = Field(
        ...,
        description="Email address to verify"
    )


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    
    email: EmailStr = Field(
        ...,
        description="Email address for password reset"
    )


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    
    token: str = Field(
        ...,
        description="Password reset token"
    )
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="New password"
    )
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v