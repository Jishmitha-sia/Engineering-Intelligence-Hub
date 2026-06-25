"""Workspace invitations and OAuth user fields

Revision ID: 003
Revises: 002
Create Date: 2026-06-19

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("oauth_provider", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("oauth_subject", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_users_oauth_provider"), "users", ["oauth_provider"])
    op.create_index(op.f("ix_users_oauth_subject"), "users", ["oauth_subject"])

    op.create_table(
        "workspace_invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("invitee_user_id", sa.Integer(), nullable=True),
        sa.Column("invited_by", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'accepted', 'declined', 'cancelled')",
            name=op.f("ck_workspace_invitations_status"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_workspace_invitations_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["invitee_user_id"],
            ["users.id"],
            name=op.f("fk_workspace_invitations_invitee_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["invited_by"],
            ["users.id"],
            name=op.f("fk_workspace_invitations_invited_by_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspace_invitations")),
    )
    op.create_index(
        op.f("ix_workspace_invitations_workspace_id"),
        "workspace_invitations",
        ["workspace_id"],
    )
    op.create_index(
        op.f("ix_workspace_invitations_email"),
        "workspace_invitations",
        ["email"],
    )
    op.create_index(
        op.f("ix_workspace_invitations_invitee_user_id"),
        "workspace_invitations",
        ["invitee_user_id"],
    )
    op.create_index(
        op.f("ix_workspace_invitations_invited_by"),
        "workspace_invitations",
        ["invited_by"],
    )
    op.create_index(
        op.f("ix_workspace_invitations_id"),
        "workspace_invitations",
        ["id"],
    )
    op.create_index(
        "uq_workspace_invitations_pending_email",
        "workspace_invitations",
        ["workspace_id", "email"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    op.drop_index("uq_workspace_invitations_pending_email", table_name="workspace_invitations")
    op.drop_index(op.f("ix_workspace_invitations_id"), table_name="workspace_invitations")
    op.drop_index(op.f("ix_workspace_invitations_invited_by"), table_name="workspace_invitations")
    op.drop_index(
        op.f("ix_workspace_invitations_invitee_user_id"),
        table_name="workspace_invitations",
    )
    op.drop_index(op.f("ix_workspace_invitations_email"), table_name="workspace_invitations")
    op.drop_index(
        op.f("ix_workspace_invitations_workspace_id"),
        table_name="workspace_invitations",
    )
    op.drop_table("workspace_invitations")
    op.drop_index(op.f("ix_users_oauth_subject"), table_name="users")
    op.drop_index(op.f("ix_users_oauth_provider"), table_name="users")
    op.drop_column("users", "oauth_subject")
    op.drop_column("users", "oauth_provider")
