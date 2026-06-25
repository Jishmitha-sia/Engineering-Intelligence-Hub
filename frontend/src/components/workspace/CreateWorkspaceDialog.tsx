"use client";

import { FormEvent, useState } from "react";
import { getErrorMessage } from "@/lib/api";
import { useWorkspaces } from "@/contexts/WorkspaceContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface CreateWorkspaceDialogProps {
  onCreated?: () => void;
}

export function CreateWorkspaceDialog({ onCreated }: CreateWorkspaceDialogProps) {
  const { createWorkspace } = useWorkspaces();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const reset = () => {
    setName("");
    setDescription("");
    setError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await createWorkspace(name.trim(), description.trim() || undefined);
      reset();
      setOpen(false);
      onCreated?.();
    } catch (err) {
      setError(getErrorMessage(err, "Unable to create workspace."));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!open) {
    return (
      <Button onClick={() => setOpen(true)}>Create workspace</Button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-lg">
        <h2 className="text-lg font-semibold text-slate-900">Create workspace</h2>
        <p className="mt-1 text-sm text-slate-600">
          Organize documents and knowledge for a team or project.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="workspace-name">Name</Label>
            <Input
              id="workspace-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Platform Engineering"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="workspace-description">Description</Label>
            <Input
              id="workspace-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Optional description"
            />
          </div>
          {error ? (
            <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          ) : null}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                reset();
                setOpen(false);
              }}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
