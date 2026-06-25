import { DashboardAppLayout } from "@/components/layout/DashboardAppLayout";

export default function WorkspacesRouteLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <DashboardAppLayout>{children}</DashboardAppLayout>;
}
