"use client";

import { useState } from "react";
import { Workspace } from "@/lib/workspaces";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface DeleteWorkspaceDialogProps {
  workspace: Workspace;
  isDeleting: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export function DeleteWorkspaceDialog({
  workspace,
  isDeleting,
  onCancel,
  onConfirm,
}: DeleteWorkspaceDialogProps) {
  const [confirmText, setConfirmText] = useState("");
  const isConfirmValid = confirmText === workspace.name;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
      <div
        role="alertdialog"
        aria-labelledby="delete-workspace-title"
        aria-describedby="delete-workspace-description"
        className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-lg"
      >
        <h2
          id="delete-workspace-title"
          className="text-lg font-semibold text-slate-900"
        >
          Delete workspace?
        </h2>
        <p
          id="delete-workspace-description"
          className="mt-2 text-sm text-slate-600"
        >
          <span className="font-medium text-slate-900">{workspace.name}</span>{" "}
          and its memberships will be permanently removed. This cannot be undone.
        </p>

        <div className="mt-4 space-y-2">
          <Label htmlFor="confirm-workspace-name" className="text-sm font-medium text-slate-700">
            Type <span className="font-semibold text-slate-900">{workspace.name}</span> to confirm:
          </Label>
          <Input
            id="confirm-workspace-name"
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder={workspace.name}
            disabled={isDeleting}
            className="font-mono"
            autoComplete="off"
          />
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            type="button"
            className="bg-red-600 hover:bg-red-700 disabled:bg-red-400"
            onClick={onConfirm}
            disabled={isDeleting || !isConfirmValid}
          >
            {isDeleting ? "Deleting..." : "Delete workspace"}
          </Button>
        </div>
      </div>
    </div>
  );
}
