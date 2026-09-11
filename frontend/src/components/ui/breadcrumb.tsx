import { cn } from "../../lib/utils";

export function Breadcrumb({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <nav
      aria-label="Breadcrumb"
      className={cn("flex items-center gap-2 text-sm text-ink/45", className)}
    >
      {children}
    </nav>
  );
}
export function BreadcrumbItem({
  children,
  active = false,
}: {
  children: React.ReactNode;
  active?: boolean;
}) {
  return <span className={active ? "text-ink" : undefined}>{children}</span>;
}
export function BreadcrumbSeparator() {
  return <span>/</span>;
}
