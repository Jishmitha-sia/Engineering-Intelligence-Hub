import { DashboardAppLayout } from "@/components/layout/DashboardAppLayout";

export default function DashboardRouteLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <DashboardAppLayout>{children}</DashboardAppLayout>;
}
