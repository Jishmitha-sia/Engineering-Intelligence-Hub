"""
Workspace API endpoints.
"""

import logging
from typing import Any, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_active_user, get_db
from models.user import User
from schemas.workspace import (
    WorkspaceCreate,
    WorkspaceDetailResponse,
    WorkspaceInvitationActionResponse,
    WorkspaceInvitationResponse,
    WorkspaceListResponse,
    WorkspaceMemberInvite,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from services.workspace_service import WorkspaceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("/invitations/me", response_model=List[WorkspaceInvitationResponse])
async def list_my_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    return await service.list_invitations_for_user(db, current_user)


@router.post(
    "/invitations/{invitation_id}/accept",
    response_model=WorkspaceInvitationActionResponse,
)
async def accept_invitation(
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    invitation = await service.accept_invitation(db, invitation_id, current_user)
    return {
        "success": True,
        "message": "Invitation accepted",
        "invitation": invitation,
    }


@router.post(
    "/invitations/{invitation_id}/decline",
    response_model=WorkspaceInvitationActionResponse,
)
async def decline_invitation(
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    invitation = await service.decline_invitation(db, invitation_id, current_user)
    return {
        "success": True,
        "message": "Invitation declined",
        "invitation": invitation,
    }


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_create: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    return await service.create_workspace(db, current_user, workspace_create)


@router.get("", response_model=WorkspaceListResponse)
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    workspaces = await service.list_workspaces(db, current_user.id)
    return {"workspaces": workspaces, "total": len(workspaces)}


@router.get("/{workspace_id}", response_model=WorkspaceDetailResponse)
async def get_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    return await service.get_workspace(
        db, workspace_id, current_user.id, include_members=True
    )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    workspace_update: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    return await service.update_workspace(
        db, workspace_id, current_user.id, workspace_update
    )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = WorkspaceService()
    await service.delete_workspace(db, workspace_id, current_user.id)


@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
async def list_workspace_members(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    members = await service.list_members(db, workspace_id, current_user.id)
    return members


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_workspace_member(
    workspace_id: int,
    invite: WorkspaceMemberInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = WorkspaceService()
    return await service.send_invitation(
        db, workspace_id, current_user.id, invite.email
    )


@router.delete(
    "/{workspace_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_workspace_invitation(
    workspace_id: int,
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = WorkspaceService()
    await service.cancel_invitation(
        db, workspace_id, invitation_id, current_user.id
    )


@router.delete(
    "/{workspace_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_workspace_member(
    workspace_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = WorkspaceService()
    await service.remove_member(db, workspace_id, current_user.id, user_id)
