"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-600">Loading your workspace...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              Engineering Intelligence Hub
            </h1>
            <p className="text-sm text-slate-500">
              Signed in as {user.full_name || user.email}
            </p>
          </div>
          <Button variant="outline" onClick={() => void logout()}>
            Sign out
          </Button>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-semibold text-slate-900">
            Welcome to Phase 1
          </h2>
          <p className="mt-3 max-w-2xl text-slate-600">
            Authentication is working end-to-end. Workspace management, document
            ingestion, and RAG chat will be added in the next phases.
          </p>
        </section>
      </main>
    </div>
  );
}
