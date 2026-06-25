"use client";

import { useEffect, useState } from "react";
import { getErrorMessage } from "@/lib/api";
import { WorkspaceInvitation } from "@/lib/workspaces";
import { useWorkspaces } from "@/contexts/WorkspaceContext";
import { Button } from "@/components/ui/button";

export function PendingInvitations() {
  const { listMyInvitations, acceptInvitation, declineInvitation } =
    useWorkspaces();
  const [invitations, setInvitations] = useState<WorkspaceInvitation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [actingOnId, setActingOnId] = useState<number | null>(null);

  const loadInvitations = async () => {
    try {
      const pending = await listMyInvitations();
      setInvitations(pending);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load invitations."));
    }
  };

  useEffect(() => {
    void loadInvitations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAccept = async (invitationId: number) => {
    setActingOnId(invitationId);
    setError(null);
    try {
      await acceptInvitation(invitationId);
      await loadInvitations();
    } catch (err) {
      setError(getErrorMessage(err, "Unable to accept invitation."));
    } finally {
      setActingOnId(null);
    }
  };

  const handleDecline = async (invitationId: number) => {
    setActingOnId(invitationId);
    setError(null);
    try {
      await declineInvitation(invitationId);
      await loadInvitations();
    } catch (err) {
      setError(getErrorMessage(err, "Unable to decline invitation."));
    } finally {
      setActingOnId(null);
    }
  };

  if (invitations.length === 0 && !error) {
    return null;
  }

  return (
    <section className="rounded-xl border border-amber-200 bg-amber-50 p-6">
      <h3 className="text-lg font-semibold text-slate-900">
        Pending invitations
      </h3>
      <p className="mt-1 text-sm text-slate-600">
        You have been invited to join these workspaces.
      </p>

      {error ? (
        <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      ) : null}

      <ul className="mt-4 space-y-3">
        {invitations.map((invitation) => (
          <li
            key={invitation.id}
            className="flex flex-col gap-3 rounded-lg border border-amber-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p className="font-medium text-slate-900">
                {invitation.workspace_name || `Workspace #${invitation.workspace_id}`}
              </p>
              <p className="text-sm text-slate-500">
                Invited to join as member
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                disabled={actingOnId === invitation.id}
                onClick={() => void handleAccept(invitation.id)}
              >
                Accept
              </Button>
              <Button
                size="sm"
                variant="outline"
                disabled={actingOnId === invitation.id}
                onClick={() => void handleDecline(invitation.id)}
              >
                Decline
              </Button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
