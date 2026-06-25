"""
Pydantic schemas for workspace operations.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class WorkspaceMemberUser(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class WorkspaceMemberResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role: str
    joined_at: datetime
    user: WorkspaceMemberUser

    class Config:
        from_attributes = True


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    role: str
    member_count: int

    class Config:
        from_attributes = True


class WorkspaceInvitationResponse(BaseModel):
    id: int
    workspace_id: int
    email: str
    status: str
    invited_by: int
    created_at: datetime
    responded_at: Optional[datetime] = None
    invitee_user_id: Optional[int] = None
    invitee_name: Optional[str] = None
    workspace_name: Optional[str] = None

    class Config:
        from_attributes = True


class WorkspaceDetailResponse(WorkspaceResponse):
    members: List[WorkspaceMemberResponse] = Field(default_factory=list)
    pending_invitations: List[WorkspaceInvitationResponse] = Field(default_factory=list)


class WorkspaceInvitationActionResponse(BaseModel):
    success: bool = True
    message: str
    invitation: WorkspaceInvitationResponse


class WorkspaceMemberInvite(BaseModel):
    email: EmailStr = Field(..., description="Email of the user to invite")


class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
    total: int
