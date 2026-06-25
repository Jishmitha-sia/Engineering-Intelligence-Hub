"use client";

import { FormEvent, useEffect, useState } from "react";
import { getErrorMessage } from "@/lib/api";
import { Workspace, WorkspaceInvitation, WorkspaceMember } from "@/lib/workspaces";
import { useWorkspaces } from "@/contexts/WorkspaceContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface MemberManagerProps {
  workspace: Workspace;
}

export function MemberManager({ workspace }: MemberManagerProps) {
  const {
    getWorkspaceDetail,
    inviteMember,
    cancelInvitation,
    removeMember,
  } = useWorkspaces();
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [pendingInvitations, setPendingInvitations] = useState<WorkspaceInvitation[]>([]);
  const [inviteEmail, setInviteEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isOwner = workspace.role === "owner";

  const reload = async () => {
    const detail = await getWorkspaceDetail(workspace.id);
    setMembers(detail.members);
    setPendingInvitations(detail.pending_invitations || []);
    // Don't call refreshWorkspaces here - it causes infinite loops
  };

  useEffect(() => {
    const loadMembers = async () => {
      try {
        await reload();
      } catch (err) {
        setError(getErrorMessage(err, "Failed to load members."));
      }
    };

    void loadMembers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspace.id]); // Only depend on workspace.id, not the callback functions

  const handleInvite = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const invitation = await inviteMember(workspace.id, inviteEmail.trim());
      setInviteEmail("");
      setSuccess(`Invitation sent to ${invitation.email}. They must accept before joining.`);
      await reload();
    } catch (err) {
      setError(getErrorMessage(err, "Unable to send invitation."));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelInvitation = async (invitationId: number) => {
    setError(null);
    try {
      await cancelInvitation(workspace.id, invitationId);
      await reload();
    } catch (err) {
      setError(getErrorMessage(err, "Unable to cancel invitation."));
    }
  };

  const handleRemove = async (userId: number) => {
    setError(null);
    try {
      await removeMember(workspace.id, userId);
      await reload();
    } catch (err) {
      setError(getErrorMessage(err, "Unable to remove member."));
    }
  };

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6">
      <h3 className="text-lg font-semibold text-slate-900">
        Members of {workspace.name}
      </h3>

      {error ? (
        <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      ) : null}

      {success ? (
        <p className="mt-4 rounded-md border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700">
          {success}
        </p>
      ) : null}

      <div className="mt-4">
        <h4 className="text-sm font-medium text-slate-700">Active members</h4>
        <ul className="mt-2 divide-y divide-slate-100">
          {members.map((member) => (
            <li
              key={member.id}
              className="flex items-center justify-between gap-4 py-3"
            >
              <div>
                <p className="font-medium text-slate-900">
                  {member.user.full_name || member.user.email}
                </p>
                <p className="text-sm text-slate-500">{member.user.email}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-slate-100 px-2 py-1 text-xs capitalize text-slate-700">
                  {member.role}
                </span>
                {isOwner && member.role !== "owner" ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => void handleRemove(member.user_id)}
                  >
                    Remove
                  </Button>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      </div>

      {isOwner && pendingInvitations.length > 0 ? (
        <div className="mt-6">
          <h4 className="text-sm font-medium text-slate-700">Pending invitations</h4>
          <ul className="mt-2 divide-y divide-slate-100">
            {pendingInvitations.map((invitation) => (
              <li
                key={invitation.id}
                className="flex items-center justify-between gap-4 py-3"
              >
                <div>
                  <p className="font-medium text-slate-900">{invitation.email}</p>
                  <p className="text-sm text-slate-500">
                    Waiting for them to accept
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-medium text-amber-800">
                    Pending
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => void handleCancelInvitation(invitation.id)}
                  >
                    Cancel
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {isOwner ? (
        <form onSubmit={handleInvite} className="mt-6 flex flex-col gap-3 sm:flex-row">
          <div className="flex-1 space-y-2">
            <Label htmlFor={`invite-email-${workspace.id}`}>Invite by email</Label>
            <Input
              id={`invite-email-${workspace.id}`}
              type="email"
              value={inviteEmail}
              onChange={(event) => setInviteEmail(event.target.value)}
              placeholder="teammate@company.com"
              required
            />
            <p className="text-xs text-slate-500">
              An invitation is sent in-app. They must accept before joining.
            </p>
          </div>
          <Button type="submit" className="sm:self-end" disabled={isSubmitting}>
            {isSubmitting ? "Sending..." : "Send invitation"}
          </Button>
        </form>
      ) : (
        <p className="mt-4 text-sm text-slate-500">
          Only workspace owners can invite or remove members.
        </p>
      )}
    </section>
  );
}
