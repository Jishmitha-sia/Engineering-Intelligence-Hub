"""
Workspace service for CRUD and membership management.
"""

from datetime import datetime
import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import User
from models.workspace import (
    InvitationStatus,
    Workspace,
    WorkspaceInvitation,
    WorkspaceMember,
    WorkspaceRole,
)
from schemas.workspace import WorkspaceCreate, WorkspaceUpdate

logger = logging.getLogger(__name__)


class WorkspaceService:
    """Business logic for workspaces and members."""

    async def get_membership(
        self,
        db: AsyncSession,
        workspace_id: int,
        user_id: int,
    ) -> Optional[WorkspaceMember]:
        result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def require_membership(
        self,
        db: AsyncSession,
        workspace_id: int,
        user_id: int,
        required_role: Optional[WorkspaceRole] = None,
    ) -> WorkspaceMember:
        member = await self.get_membership(db, workspace_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this workspace is forbidden",
            )
        if required_role == WorkspaceRole.OWNER and member.role != WorkspaceRole.OWNER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Owner role required for this action",
            )
        return member

    async def _workspace_to_response(
        self,
        db: AsyncSession,
        workspace: Workspace,
        user_id: int,
    ) -> dict:
        membership = await self.get_membership(db, workspace.id, user_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this workspace is forbidden",
            )

        count_result = await db.execute(
            select(func.count())
            .select_from(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace.id)
        )
        member_count = count_result.scalar_one()

        return {
            "id": workspace.id,
            "name": workspace.name,
            "description": workspace.description,
            "created_by": workspace.created_by,
            "created_at": workspace.created_at,
            "updated_at": workspace.updated_at,
            "role": membership.role,
            "member_count": member_count,
        }

    async def create_workspace(
        self,
        db: AsyncSession,
        user: User,
        workspace_create: WorkspaceCreate,
    ) -> dict:
        workspace = Workspace(
            name=workspace_create.name.strip(),
            description=workspace_create.description,
            created_by=user.id,
        )
        db.add(workspace)
        await db.flush()

        owner_membership = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER.value,
        )
        db.add(owner_membership)
        await db.commit()
        await db.refresh(workspace)

        logger.info("Workspace created: %s (ID: %s) by user %s", workspace.name, workspace.id, user.id)
        return await self._workspace_to_response(db, workspace, user.id)

    async def list_workspaces(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[dict]:
        result = await db.execute(
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.updated_at.desc())
        )
        workspaces = result.scalars().unique().all()
        return [await self._workspace_to_response(db, workspace, user_id) for workspace in workspaces]

    async def get_workspace(
        self,
        db: AsyncSession,
        workspace_id: int,
        user_id: int,
        include_members: bool = False,
    ) -> dict:
        await self.require_membership(db, workspace_id, user_id)

        query = select(Workspace).where(Workspace.id == workspace_id)
        if include_members:
            query = query.options(
                selectinload(Workspace.members).selectinload(WorkspaceMember.user)
            )

        result = await db.execute(query)
        workspace = result.scalar_one_or_none()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        response = await self._workspace_to_response(db, workspace, user_id)
        if include_members:
            response["members"] = workspace.members
            membership = await self.get_membership(db, workspace_id, user_id)
            if membership and membership.role == WorkspaceRole.OWNER.value:
                response["pending_invitations"] = await self.list_pending_invitations(
                    db, workspace_id, user_id
                )
            else:
                response["pending_invitations"] = []
        return response

    async def update_workspace(
        self,
        db: AsyncSession,
        workspace_id: int,
        user_id: int,
        workspace_update: WorkspaceUpdate,
    ) -> dict:
        await self.require_membership(
            db, workspace_id, user_id, required_role=WorkspaceRole.OWNER
        )

        result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
        workspace = result.scalar_one_or_none()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        update_data = workspace_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "name" in update_data and update_data["name"] is not None:
            workspace.name = update_data["name"].strip()
        if "description" in update_data:
            workspace.description = update_data["description"]

        await db.commit()
        await db.refresh(workspace)
        logger.info("Workspace updated: ID %s by user %s", workspace_id, user_id)
        return await self._workspace_to_response(db, workspace, user_id)

    async def delete_workspace(
        self,
        db: AsyncSession,
        workspace_id: int,
        user_id: int,
    ) -> None:
        await self.require_membership(
            db, workspace_id, user_id, required_role=WorkspaceRole.OWNER
        )

        result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
        workspace = result.scalar_one_or_none()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        await db.delete(workspace)
        await db.commit()
        logger.info("Workspace deleted: ID %s by user %s", workspace_id, user_id)

    def _invitation_to_dict(
        self,
        invitation: WorkspaceInvitation,
        workspace_name: Optional[str] = None,
        invitee_name: Optional[str] = None,
    ) -> dict:
        return {
            "id": invitation.id,
            "workspace_id": invitation.workspace_id,
            "email": invitation.email,
            "status": invitation.status,
            "invited_by": invitation.invited_by,
            "created_at": invitation.created_at,
            "responded_at": invitation.responded_at,
            "invitee_user_id": invitation.invitee_user_id,
            "invitee_name": invitee_name,
            "workspace_name": workspace_name,
        }

    async def _get_pending_invitation(
        self,
        db: AsyncSession,
        workspace_id: int,
        email: str,
    ) -> Optional[WorkspaceInvitation]:
        result = await db.execute(
            select(WorkspaceInvitation).where(
                WorkspaceInvitation.workspace_id == workspace_id,
                WorkspaceInvitation.email == email.lower(),
                WorkspaceInvitation.status == InvitationStatus.PENDING.value,
            )
        )
        return result.scalar_one_or_none()

    async def send_invitation(
        self,
        db: AsyncSession,
        workspace_id: int,
        inviter_id: int,
        email: str,
    ) -> dict:
        await self.require_membership(
            db, workspace_id, inviter_id, required_role=WorkspaceRole.OWNER
        )

        normalized_email = email.lower().strip()
        inviter = await db.get(User, inviter_id)
        if inviter and inviter.email == normalized_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot invite yourself",
            )

        user_result = await db.execute(
            select(User).where(User.email == normalized_email)
        )
        invited_user = user_result.scalar_one_or_none()
        if invited_user:
            existing = await self.get_membership(db, workspace_id, invited_user.id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a member of this workspace",
                )

        pending = await self._get_pending_invitation(db, workspace_id, normalized_email)
        if pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An invitation is already pending for this email",
            )

        invitation = WorkspaceInvitation(
            workspace_id=workspace_id,
            email=normalized_email,
            invitee_user_id=invited_user.id if invited_user else None,
            invited_by=inviter_id,
            status=InvitationStatus.PENDING.value,
        )
        db.add(invitation)
        await db.commit()
        await db.refresh(invitation)

        logger.info(
            "Invitation sent to %s for workspace %s by user %s",
            normalized_email,
            workspace_id,
            inviter_id,
        )
        invitee_name = invited_user.full_name if invited_user else None
        return self._invitation_to_dict(invitation, invitee_name=invitee_name)

    async def list_pending_invitations(
        self,
        db: AsyncSession,
        workspace_id: int,
        user_id: int,
    ) -> List[dict]:
        await self.require_membership(
            db, workspace_id, user_id, required_role=WorkspaceRole.OWNER
        )

        result = await db.execute(
            select(WorkspaceInvitation)
            .options(selectinload(WorkspaceInvitation.invitee))
            .where(
                WorkspaceInvitation.workspace_id == workspace_id,
                WorkspaceInvitation.status == InvitationStatus.PENDING.value,
            )
            .order_by(WorkspaceInvitation.created_at.asc())
        )
        return [
            self._invitation_to_dict(
                inv,
                invitee_name=inv.invitee.full_name if inv.invitee else None,
            )
            for inv in result.scalars().all()
        ]

    async def list_invitations_for_user(
        self,
        db: AsyncSession,
        user: User,
    ) -> List[dict]:
        result = await db.execute(
            select(WorkspaceInvitation)
            .options(
                selectinload(WorkspaceInvitation.workspace),
                selectinload(WorkspaceInvitation.invitee),
            )
            .where(
                WorkspaceInvitation.status == InvitationStatus.PENDING.value,
                or_(
                    WorkspaceInvitation.email == user.email.lower(),
                    WorkspaceInvitation.invitee_user_id == user.id,
                ),
            )
            .order_by(WorkspaceInvitation.created_at.desc())
        )
        return [
            self._invitation_to_dict(
                inv,
                workspace_name=inv.workspace.name,
                invitee_name=inv.invitee.full_name if inv.invitee else None,
            )
            for inv in result.scalars().all()
        ]

    async def _get_invitation_for_user(
        self,
        db: AsyncSession,
        invitation_id: int,
        user: User,
    ) -> WorkspaceInvitation:
        result = await db.execute(
            select(WorkspaceInvitation)
            .options(selectinload(WorkspaceInvitation.workspace))
            .where(WorkspaceInvitation.id == invitation_id)
        )
        invitation = result.scalar_one_or_none()
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )
        if invitation.status != InvitationStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation is no longer pending",
            )
        if (
            invitation.email != user.email.lower()
            and invitation.invitee_user_id != user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This invitation is not for your account",
            )
        return invitation

    async def accept_invitation(
        self,
        db: AsyncSession,
        invitation_id: int,
        user: User,
    ) -> dict:
        invitation = await self._get_invitation_for_user(db, invitation_id, user)

        existing = await self.get_membership(db, invitation.workspace_id, user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this workspace",
            )

        membership = WorkspaceMember(
            workspace_id=invitation.workspace_id,
            user_id=user.id,
            role=WorkspaceRole.MEMBER.value,
        )
        invitation.status = InvitationStatus.ACCEPTED.value
        invitation.invitee_user_id = user.id
        invitation.responded_at = datetime.utcnow()
        db.add(membership)
        await db.commit()
        await db.refresh(invitation)

        logger.info("User %s accepted invitation %s", user.email, invitation_id)
        workspace_name = invitation.workspace.name if invitation.workspace else None
        return self._invitation_to_dict(
            invitation,
            workspace_name=workspace_name,
            invitee_name=user.full_name,
        )

    async def decline_invitation(
        self,
        db: AsyncSession,
        invitation_id: int,
        user: User,
    ) -> dict:
        invitation = await self._get_invitation_for_user(db, invitation_id, user)
        invitation.status = InvitationStatus.DECLINED.value
        invitation.invitee_user_id = user.id
        invitation.responded_at = datetime.utcnow()
        await db.commit()
        await db.refresh(invitation)

        logger.info("User %s declined invitation %s", user.email, invitation_id)
        workspace_name = invitation.workspace.name if invitation.workspace else None
        return self._invitation_to_dict(
            invitation,
            workspace_name=workspace_name,
            invitee_name=user.full_name,
        )

    async def cancel_invitation(
        self,
        db: AsyncSession,
        workspace_id: int,
        invitation_id: int,
        actor_id: int,
    ) -> None:
        await self.require_membership(
            db, workspace_id, actor_id, required_role=WorkspaceRole.OWNER
        )

        result = await db.execute(
            select(WorkspaceInvitation).where(
                WorkspaceInvitation.id == invitation_id,
                WorkspaceInvitation.workspace_id == workspace_id,
            )
        )
        invitation = result.scalar_one_or_none()
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )
        if invitation.status != InvitationStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending invitations can be cancelled",
            )

        invitation.status = InvitationStatus.CANCELLED.value
        invitation.responded_at = datetime.utcnow()
        await db.commit()
        logger.info(
            "Invitation %s cancelled for workspace %s by user %s",
            invitation_id,
            workspace_id,
            actor_id,
        )

    async def invite_member(
        self,
        db: AsyncSession,
        workspace_id: int,
        inviter_id: int,
        email: str,
    ) -> dict:
        return await self.send_invitation(db, workspace_id, inviter_id, email)

    async def list_members(
        self,
        db: AsyncSession,
        workspace_id: int,
        user_id: int,
    ) -> List[WorkspaceMember]:
        await self.require_membership(db, workspace_id, user_id)

        result = await db.execute(
            select(WorkspaceMember)
            .options(selectinload(WorkspaceMember.user))
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.joined_at.asc())
        )
        return list(result.scalars().all())

    async def remove_member(
        self,
        db: AsyncSession,
        workspace_id: int,
        actor_id: int,
        target_user_id: int,
    ) -> None:
        await self.require_membership(
            db, workspace_id, actor_id, required_role=WorkspaceRole.OWNER
        )

        target = await self.get_membership(db, workspace_id, target_user_id)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found in this workspace",
            )

        if target.role == WorkspaceRole.OWNER.value:
            owners_result = await db.execute(
                select(func.count())
                .select_from(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.role == WorkspaceRole.OWNER.value,
                )
            )
            owner_count = owners_result.scalar_one()
            if owner_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last owner of a workspace",
                )

        await db.delete(target)
        await db.commit()
        logger.info(
            "User %s removed from workspace %s by user %s",
            target_user_id,
            workspace_id,
            actor_id,
        )
