"""
User model for Engineering Intelligence Hub.

Defines the User SQLAlchemy model with authentication support.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional, List

from db.base import Base, TimestampMixin, ActiveMixin


class User(Base, TimestampMixin, ActiveMixin):
    """
    User model for authentication and user management.
    
    Attributes:
        id: Primary key
        email: Unique email address for login
        hashed_password: BCrypt hashed password
        full_name: User's full name
        is_active: Whether user account is active
        is_verified: Whether email is verified
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login_at: Last login timestamp
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    
    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False,
        doc="Unique email address for login"
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        doc="BCrypt hashed password"
    )
    
    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True,
        doc="User's full name"
    )
    
    # Status fields (is_active inherited from ActiveMixin)
    is_verified: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False,
        doc="Whether email address is verified"
    )
    
    # Activity tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last login timestamp"
    )
    
    # Relationships (will be added in Phase 2)
    # workspaces: Mapped[List["WorkspaceMember"]] = relationship(
    #     "WorkspaceMember", back_populates="user"
    # )
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"
    
    def to_dict(self) -> dict:
        """Convert User to dictionary (excluding sensitive fields)."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
    
    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for this model."""
        return cls.__tablename__