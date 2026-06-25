"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { apiRequest } from "@/lib/api";
import {
  Workspace,
  WorkspaceDetail,
  WorkspaceInvitation,
  WorkspaceListResponse,
  WorkspaceMember,
  getStoredWorkspaceId,
  setStoredWorkspaceId,
} from "@/lib/workspaces";
import { useAuth } from "@/contexts/AuthContext";

interface WorkspaceContextValue {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  isLoading: boolean;
  error: string | null;
  refreshWorkspaces: () => Promise<void>;
  selectWorkspace: (workspaceId: number) => void;
  createWorkspace: (name: string, description?: string) => Promise<Workspace>;
  updateWorkspace: (
    workspaceId: number,
    data: { name?: string; description?: string },
  ) => Promise<Workspace>;
  deleteWorkspace: (workspaceId: number) => Promise<void>;
  getWorkspaceDetail: (workspaceId: number) => Promise<WorkspaceDetail>;
  inviteMember: (workspaceId: number, email: string) => Promise<WorkspaceInvitation>;
  cancelInvitation: (workspaceId: number, invitationId: number) => Promise<void>;
  listMyInvitations: () => Promise<WorkspaceInvitation[]>;
  acceptInvitation: (invitationId: number) => Promise<void>;
  declineInvitation: (invitationId: number) => Promise<void>;
  removeMember: (workspaceId: number, userId: number) => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextValue | undefined>(
  undefined,
);

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const { token, user } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspaceId, setCurrentWorkspaceId] = useState<number | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshWorkspaces = useCallback(async () => {
    if (!token) {
      setWorkspaces([]);
      setCurrentWorkspaceId(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiRequest<WorkspaceListResponse>(
        "/api/v1/workspaces",
        { method: "GET" },
        token,
      );
      setWorkspaces(response.workspaces);

      const storedId = getStoredWorkspaceId();
      const validStored = response.workspaces.find((w) => w.id === storedId);
      const nextId = validStored?.id ?? response.workspaces[0]?.id ?? null;
      setCurrentWorkspaceId(nextId);
      setStoredWorkspaceId(nextId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workspaces");
      setWorkspaces([]);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (user && token) {
      void refreshWorkspaces();
    } else {
      setWorkspaces([]);
      setCurrentWorkspaceId(null);
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, token]);

  const selectWorkspace = useCallback((workspaceId: number) => {
    setCurrentWorkspaceId(workspaceId);
    setStoredWorkspaceId(workspaceId);
  }, []);

  const createWorkspace = useCallback(
    async (name: string, description?: string) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      const workspace = await apiRequest<Workspace>(
        "/api/v1/workspaces",
        {
          method: "POST",
          body: JSON.stringify({ name, description: description || null }),
        },
        token,
      );
      setWorkspaces((prev) => [workspace, ...prev]);
      selectWorkspace(workspace.id);
      return workspace;
    },
    [selectWorkspace, token],
  );

  const updateWorkspace = useCallback(
    async (
      workspaceId: number,
      data: { name?: string; description?: string },
    ) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      const workspace = await apiRequest<Workspace>(
        `/api/v1/workspaces/${workspaceId}`,
        {
          method: "PUT",
          body: JSON.stringify(data),
        },
        token,
      );
      setWorkspaces((prev) =>
        prev.map((item) => (item.id === workspaceId ? workspace : item)),
      );
      return workspace;
    },
    [token],
  );

  const deleteWorkspace = useCallback(
    async (workspaceId: number) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      await apiRequest(
        `/api/v1/workspaces/${workspaceId}`,
        { method: "DELETE" },
        token,
      );

      setWorkspaces((prev) => {
        const next = prev.filter((item) => item.id !== workspaceId);
        if (currentWorkspaceId === workspaceId) {
          const nextId = next[0]?.id ?? null;
          setCurrentWorkspaceId(nextId);
          setStoredWorkspaceId(nextId);
        }
        return next;
      });
    },
    [currentWorkspaceId, token],
  );

  const getWorkspaceDetail = useCallback(
    async (workspaceId: number) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      return apiRequest<WorkspaceDetail>(
        `/api/v1/workspaces/${workspaceId}`,
        { method: "GET" },
        token,
      );
    },
    [token],
  );

  const inviteMember = useCallback(
    async (workspaceId: number, email: string) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      return apiRequest<WorkspaceInvitation>(
        `/api/v1/workspaces/${workspaceId}/members`,
        {
          method: "POST",
          body: JSON.stringify({ email }),
        },
        token,
      );
    },
    [token],
  );

  const cancelInvitation = useCallback(
    async (workspaceId: number, invitationId: number) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      await apiRequest(
        `/api/v1/workspaces/${workspaceId}/invitations/${invitationId}`,
        { method: "DELETE" },
        token,
      );
    },
    [token],
  );

  const listMyInvitations = useCallback(async () => {
    if (!token) {
      return [];
    }

    return apiRequest<WorkspaceInvitation[]>(
      "/api/v1/workspaces/invitations/me",
      { method: "GET" },
      token,
    );
  }, [token]);

  const acceptInvitation = useCallback(
    async (invitationId: number) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      await apiRequest(
        `/api/v1/workspaces/invitations/${invitationId}/accept`,
        { method: "POST" },
        token,
      );
      
      // Manually refresh workspaces after accepting invitation
      // Don't depend on refreshWorkspaces callback to avoid infinite loop
      try {
        const response = await apiRequest<WorkspaceListResponse>(
          "/api/v1/workspaces",
          { method: "GET" },
          token,
        );
        setWorkspaces(response.workspaces);

        const storedId = getStoredWorkspaceId();
        const validStored = response.workspaces.find((w) => w.id === storedId);
        const nextId = validStored?.id ?? response.workspaces[0]?.id ?? null;
        setCurrentWorkspaceId(nextId);
        setStoredWorkspaceId(nextId);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to refresh workspaces");
      }
    },
    [token],
  );

  const declineInvitation = useCallback(
    async (invitationId: number) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      await apiRequest(
        `/api/v1/workspaces/invitations/${invitationId}/decline`,
        { method: "POST" },
        token,
      );
    },
    [token],
  );

  const removeMember = useCallback(
    async (workspaceId: number, userId: number) => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      await apiRequest(
        `/api/v1/workspaces/${workspaceId}/members/${userId}`,
        { method: "DELETE" },
        token,
      );
    },
    [token],
  );

  const currentWorkspace = useMemo(
    () => workspaces.find((workspace) => workspace.id === currentWorkspaceId) ?? null,
    [workspaces, currentWorkspaceId],
  );

  const value = useMemo(
    () => ({
      workspaces,
      currentWorkspace,
      isLoading,
      error,
      refreshWorkspaces,
      selectWorkspace,
      createWorkspace,
      updateWorkspace,
      deleteWorkspace,
      getWorkspaceDetail,
      inviteMember,
      cancelInvitation,
      listMyInvitations,
      acceptInvitation,
      declineInvitation,
      removeMember,
    }),
    [
      workspaces,
      currentWorkspace,
      isLoading,
      error,
      refreshWorkspaces,
      selectWorkspace,
      createWorkspace,
      updateWorkspace,
      deleteWorkspace,
      getWorkspaceDetail,
      inviteMember,
      cancelInvitation,
      listMyInvitations,
      acceptInvitation,
      declineInvitation,
      removeMember,
    ],
  );

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspaces() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error("useWorkspaces must be used within a WorkspaceProvider");
  }
  return context;
}
