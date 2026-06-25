export const CURRENT_WORKSPACE_KEY = "eih_current_workspace_id";

export interface Workspace {
  id: number;
  name: string;
  description: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  role: "owner" | "member";
  member_count: number;
}

export interface WorkspaceMember {
  id: number;
  workspace_id: number;
  user_id: number;
  role: "owner" | "member";
  joined_at: string;
  user: {
    id: number;
    email: string;
    full_name: string | null;
  };
}

export interface WorkspaceInvitation {
  id: number;
  workspace_id: number;
  email: string;
  status: "pending" | "accepted" | "declined" | "cancelled";
  invited_by: number;
  created_at: string;
  responded_at: string | null;
  invitee_user_id: number | null;
  invitee_name: string | null;
  workspace_name: string | null;
}

export interface WorkspaceDetail extends Workspace {
  members: WorkspaceMember[];
  pending_invitations: WorkspaceInvitation[];
}

export interface WorkspaceListResponse {
  workspaces: Workspace[];
  total: number;
}

export function getStoredWorkspaceId(): number | null {
  if (typeof window === "undefined") {
    return null;
  }
  const value = localStorage.getItem(CURRENT_WORKSPACE_KEY);
  return value ? Number(value) : null;
}

export function setStoredWorkspaceId(workspaceId: number | null): void {
  if (workspaceId === null) {
    localStorage.removeItem(CURRENT_WORKSPACE_KEY);
    return;
  }
  localStorage.setItem(CURRENT_WORKSPACE_KEY, String(workspaceId));
}
