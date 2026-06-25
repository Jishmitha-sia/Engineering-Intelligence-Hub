"use client";

import Link from "next/link";
import { useWorkspaces } from "@/contexts/WorkspaceContext";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const { currentWorkspace, isLoading } = useWorkspaces();

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="text-2xl font-semibold text-slate-900">
        Welcome to Phase 2
      </h2>
      <p className="mt-3 max-w-2xl text-slate-600">
        Workspace management is live. Create a workspace, invite teammates, and
        switch between projects from the header. Document ingestion and RAG chat
        arrive in the next phases.
      </p>

      <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4">
        <p className="text-sm text-slate-600">Active workspace</p>
        <p className="mt-1 text-lg font-medium text-slate-900">
          {isLoading
            ? "Loading..."
            : currentWorkspace?.name || "No workspace selected"}
        </p>
        {currentWorkspace ? (
          <p className="mt-1 text-sm capitalize text-slate-500">
            Your role: {currentWorkspace.role}
          </p>
        ) : null}
      </div>

      <div className="mt-6">
        <Link href="/workspaces">
          <Button>Manage workspaces</Button>
        </Link>
      </div>
    </section>
  );
}
