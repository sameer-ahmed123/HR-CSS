import {
  Bell,
  BriefcaseBusiness,
  ChevronDown,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  FileText,
  ShieldCheck,
  Users,
  UserRound,
  X,
  BadgeCheck,
} from "lucide-react";
import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import type { UserRole } from "../../types";
import { Avatar, AvatarFallback } from "../../components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../../components/ui/dropdown-menu";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbSeparator,
} from "../../components/ui/breadcrumb";
import { Sheet, SheetContent } from "../../components/ui/sheet";

const navigation: {
  label: string;
  path: string;
  icon: typeof LayoutDashboard;
  roles: UserRole[];
}[] = [
  {
    label: "Overview",
    path: "/",
    icon: LayoutDashboard,
    roles: ["ADMIN", "HR", "TEAM_LEAD", "EMPLOYEE", "FINANCE"],
  },
  {
    label: "People",
    path: "/people",
    icon: Users,
    roles: ["ADMIN", "HR", "TEAM_LEAD"],
  },
  {
    label: "Documents",
    path: "/documents",
    icon: FileText,
    roles: ["ADMIN", "HR", "TEAM_LEAD", "EMPLOYEE", "FINANCE"],
  },
  {
    label: "Policies",
    path: "/policies",
    icon: BadgeCheck,
    roles: ["ADMIN", "HR", "TEAM_LEAD", "EMPLOYEE", "FINANCE"],
  },
  {
    label: "Organization",
    path: "/organization",
    icon: Settings,
    roles: ["ADMIN", "HR"],
  },
  {
    label: "Access Control",
    path: "/access-control",
    icon: ShieldCheck,
    roles: ["ADMIN", "HR"],
  },
  {
    label: "Recruitment",
    path: "/recruitment",
    icon: BriefcaseBusiness,
    roles: ["ADMIN", "HR", "TEAM_LEAD"],
  },
  {
    label: "Job Postings",
    path: "/recruitment/jobs",
    icon: BriefcaseBusiness,
    roles: ["ADMIN", "HR", "TEAM_LEAD"],
  },
  {
    label: "Hiring Requests",
    path: "/recruitment/requests",
    icon: BriefcaseBusiness,
    roles: ["TEAM_LEAD"],
  },
  {
    label: "Review Requests",
    path: "/recruitment/review",
    icon: BriefcaseBusiness,
    roles: ["ADMIN", "HR"],
  },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const visibleNavigation = navigation.filter(
    (item) => user && item.roles.includes(user.role),
  );
  const currentPage =
    visibleNavigation.find((item) => item.path === location.pathname)?.label ??
    "Access denied";
  const initials =
    `${user?.first_name?.[0] ?? ""}${user?.last_name?.[0] ?? ""}`.toUpperCase();

  return (
    <div className="min-h-screen bg-surface text-ink">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 border-r border-ink/10 bg-white px-6 py-7 text-ink lg:block">
        <SidebarContent
          visibleNavigation={visibleNavigation}
          locationPath={location.pathname}
          onNavigate={() => undefined}
        />
      </aside>
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent className="lg:hidden">
          <SidebarContent
            visibleNavigation={visibleNavigation}
            locationPath={location.pathname}
            onNavigate={() => setMobileOpen(false)}
          />
        </SheetContent>
      </Sheet>
      <div className="lg:pl-72">
        <header className="flex h-20 items-center justify-between border-b border-ink/10 bg-white/80 px-5 backdrop-blur sm:px-10">
          <button
            className="lg:hidden"
            onClick={() => setMobileOpen(true)}
            aria-label="Open navigation"
          >
            <Menu />
          </button>
          <Breadcrumb className="hidden sm:flex">
            <BreadcrumbItem>Workspace</BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem active>{currentPage}</BreadcrumbItem>
          </Breadcrumb>
          <div className="ml-auto flex items-center gap-5">
            <button
              className="relative rounded-xl p-2 text-ink/55 transition hover:bg-accent"
              aria-label="Notifications"
            >
              <Bell size={19} />
              <span className="absolute -right-1 -top-1 h-2 w-2 bg-coral" />
            </button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className="flex items-center gap-3"
                  aria-label="Open profile menu"
                >
                  <Avatar>
                    <AvatarFallback>{initials}</AvatarFallback>
                  </Avatar>
                  <span className="hidden text-left sm:block">
                    <span className="block text-sm font-semibold">
                      {user?.first_name} {user?.last_name}
                    </span>
                    <span className="block text-xs text-ink/45">
                      {user?.role}
                    </span>
                  </span>
                  <ChevronDown size={15} />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link to="/profile">
                    <UserRound size={15} />
                    Profile & security
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={logout}>
                  <LogOut size={15} />
                  Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
        <main className="p-5 sm:p-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function SidebarContent({
  visibleNavigation,
  locationPath,
  onNavigate,
}: {
  visibleNavigation: typeof navigation;
  locationPath: string;
  onNavigate: () => void;
}) {
  return (
    <>
      <div className="flex items-center justify-between">
        <Link to="/" className="font-display text-2xl font-bold tracking-tight">
          hr<span className="text-coral">.</span>css
        </Link>
        <button
          className="lg:hidden"
          onClick={onNavigate}
          aria-label="Close navigation"
        >
          <X size={20} />
        </button>
      </div>
      <p className="mt-2 text-xs uppercase tracking-[0.18em] text-ink/45">
        Corporate support system
      </p>
      <nav className="mt-14 space-y-2">
        {visibleNavigation.map(({ label, path, icon: Icon }) => (
          <Link
            key={path}
            to={path}
            onClick={onNavigate}
            className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${locationPath === path ? "bg-mint font-semibold text-ink" : "text-ink/60 hover:bg-surface hover:text-ink"}`}
          >
            <Icon size={18} />
            {label}
          </Link>
        ))}
      </nav>
      <div className="absolute bottom-7 left-6 right-6 border-t border-mist/10 pt-5 text-xs text-mist/40">
        Phase 01 / Foundations
      </div>
    </>
  );
}
