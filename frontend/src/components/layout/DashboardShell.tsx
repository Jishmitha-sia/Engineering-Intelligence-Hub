"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useWorkspaces } from "@/contexts/WorkspaceContext";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Overview" },
  { href: "/workspaces", label: "Workspaces" },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { currentWorkspace, workspaces, selectWorkspace, isLoading } =
    useWorkspaces();

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              Engineering Intelligence Hub
            </h1>
            <p className="text-sm text-slate-500">
              Signed in as {user?.full_name || user?.email}
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="flex items-center gap-2">
              <label htmlFor="workspace-switcher" className="text-sm text-slate-600">
                Workspace
              </label>
              <select
                id="workspace-switcher"
                className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
                value={currentWorkspace?.id ?? ""}
                disabled={isLoading || workspaces.length === 0}
                onChange={(event) => selectWorkspace(Number(event.target.value))}
              >
                {workspaces.length === 0 ? (
                  <option value="">No workspaces yet</option>
                ) : (
                  workspaces.map((workspace) => (
                    <option key={workspace.id} value={workspace.id}>
                      {workspace.name}
                    </option>
                  ))
                )}
              </select>
            </div>
            <Button variant="outline" onClick={() => void logout()}>
              Sign out
            </Button>
          </div>
        </div>

        <nav className="mx-auto flex max-w-6xl gap-1 px-6 pb-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                pathname === item.href
                  ? "bg-slate-900 text-white"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  );
}
