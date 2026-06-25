import { WorkspaceList } from "@/components/workspace/WorkspaceList";
import { PendingInvitations } from "@/components/workspace/PendingInvitations";

export default function WorkspacesPage() {
  return (
    <div className="space-y-8">
      <PendingInvitations />
      <WorkspaceList />
    </div>
  );
}
