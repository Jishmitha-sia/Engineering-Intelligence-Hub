"use client";

import { FormEvent, useState } from "react";
import { getErrorMessage } from "@/lib/api";
import { Workspace } from "@/lib/workspaces";
import { useWorkspaces } from "@/contexts/WorkspaceContext";
import { CreateWorkspaceDialog } from "@/components/workspace/CreateWorkspaceDialog";
import { WorkspaceCard } from "@/components/workspace/WorkspaceCard";
import { MemberManager } from "@/components/workspace/MemberManager";
import { DeleteWorkspaceDialog } from "@/components/workspace/DeleteWorkspaceDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function WorkspaceList() {
  const {
    workspaces,
    currentWorkspace,
    isLoading,
    error,
    selectWorkspace,
    updateWorkspace,
    deleteWorkspace,
  } = useWorkspaces();

  const [editingWorkspace, setEditingWorkspace] = useState<Workspace | null>(null);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [workspaceToDelete, setWorkspaceToDelete] = useState<Workspace | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const activeWorkspaceId = currentWorkspace?.id ?? null;
  const activeWorkspace = workspaces.find((w) => w.id === activeWorkspaceId) ?? null;

  const handleEdit = (workspace: Workspace) => {
    setEditingWorkspace(workspace);
    setEditName(workspace.name);
    setEditDescription(workspace.description || "");
    setActionError(null);
  };

  const handleUpdate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!editingWorkspace) {
      return;
    }

    setIsSubmitting(true);
    setActionError(null);

    try {
      await updateWorkspace(editingWorkspace.id, {
        name: editName.trim(),
        description: editDescription.trim() || undefined,
      });
      setEditingWorkspace(null);
      // No need to call refreshWorkspaces - updateWorkspace already updates state
    } catch (err) {
      setActionError(getErrorMessage(err, "Unable to update workspace."));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteRequest = (workspace: Workspace) => {
    setActionError(null);
    setWorkspaceToDelete(workspace);
  };

  const handleDeleteConfirm = async () => {
    if (!workspaceToDelete) {
      return;
    }

    setIsDeleting(true);
    setActionError(null);

    try {
      await deleteWorkspace(workspaceToDelete.id);
      setWorkspaceToDelete(null);
      // No need to call refreshWorkspaces - deleteWorkspace already updates state
    } catch (err) {
      setActionError(getErrorMessage(err, "Unable to delete workspace."));
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return <p className="text-slate-600">Loading workspaces...</p>;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Workspaces</h2>
          <p className="mt-1 text-slate-600">
            Create teams, invite members, and switch between projects.
          </p>
        </div>
        <CreateWorkspaceDialog />
      </div>

      {error ? (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      ) : null}

      {actionError ? (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {actionError}
        </p>
      ) : null}

      {workspaces.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center">
          <p className="text-slate-600">
            No workspaces yet. Create your first workspace to get started.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {workspaces.map((workspace) => (
            <WorkspaceCard
              key={workspace.id}
              workspace={workspace}
              isActive={workspace.id === activeWorkspaceId}
              onSelect={selectWorkspace}
              onEdit={handleEdit}
              onDelete={handleDeleteRequest}
            />
          ))}
        </div>
      )}

      {editingWorkspace ? (
        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <h3 className="text-lg font-semibold text-slate-900">Edit workspace</h3>
          <form onSubmit={handleUpdate} className="mt-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Name</Label>
              <Input
                id="edit-name"
                value={editName}
                onChange={(event) => setEditName(event.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Input
                id="edit-description"
                value={editDescription}
                onChange={(event) => setEditDescription(event.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={isSubmitting}>
                Save changes
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditingWorkspace(null)}
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      ) : null}

      {activeWorkspace ? <MemberManager workspace={activeWorkspace} /> : null}

      {workspaceToDelete ? (
        <DeleteWorkspaceDialog
          workspace={workspaceToDelete}
          isDeleting={isDeleting}
          onCancel={() => {
            if (!isDeleting) {
              setWorkspaceToDelete(null);
            }
          }}
          onConfirm={() => void handleDeleteConfirm()}
        />
      ) : null}
    </div>
  );
}
