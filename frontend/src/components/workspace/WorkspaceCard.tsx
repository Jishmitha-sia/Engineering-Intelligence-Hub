"use client";

import { Workspace } from "@/lib/workspaces";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface WorkspaceCardProps {
  workspace: Workspace;
  isActive: boolean;
  onSelect: (workspaceId: number) => void;
  onEdit?: (workspace: Workspace) => void;
  onDelete?: (workspace: Workspace) => void;
}

export function WorkspaceCard({
  workspace,
  isActive,
  onSelect,
  onEdit,
  onDelete,
}: WorkspaceCardProps) {
  const isOwner = workspace.role === "owner";

  return (
    <Card className={isActive ? "border-slate-900" : undefined}>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle>{workspace.name}</CardTitle>
            <CardDescription>
              {workspace.description || "No description"}
            </CardDescription>
          </div>
          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium capitalize text-slate-700">
            {workspace.role}
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-slate-600">
          {workspace.member_count} member
          {workspace.member_count === 1 ? "" : "s"}
        </p>
        <div className="flex flex-wrap gap-2">
          <Button
            variant={isActive ? "default" : "outline"}
            size="sm"
            onClick={() => onSelect(workspace.id)}
          >
            {isActive ? "Active" : "Switch to"}
          </Button>
          {isOwner && onEdit ? (
            <Button variant="outline" size="sm" onClick={() => onEdit(workspace)}>
              Edit
            </Button>
          ) : null}
          {isOwner && onDelete ? (
            <Button
              variant="outline"
              size="sm"
              className="text-red-700 hover:text-red-800"
              onClick={() => onDelete(workspace)}
            >
              Delete
            </Button>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
