import { Filter, Search, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { authApi } from "../api/auth";
import { Alert } from "../components/ui/alert";
import { Badge } from "../components/ui/badge";
import { Card, CardContent } from "../components/ui/card";
import InviteMemberDialog from "../components/organization/InviteMemberDialog";
import { useAuth } from "../context/AuthContext";
import type { OrganizationUser } from "../types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";

export default function PeoplePage() {
  const { user } = useAuth();
  const [people, setPeople] = useState<OrganizationUser[]>([]);
  const [query, setQuery] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("all");
  const [roleFilter, setRoleFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [joinedFrom, setJoinedFrom] = useState("");
  const [joinedTo, setJoinedTo] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const canInvite = user?.role === "ADMIN" || user?.role === "HR";
  const canFilter = canInvite;

  useEffect(() => {
    async function loadPeople() {
      try {
        const { data } = await authApi.listOrganizationUsers();
        setPeople(data);
      } catch {
        setError("We could not load the people directory. Please try again.");
      } finally {
        setLoading(false);
      }
    }
    void loadPeople();
  }, []);

  const filteredPeople = people.filter((person) => {
    const searchable =
      `${person.first_name} ${person.last_name} ${person.email} ${person.role} ${person.department_name ?? ""}`.toLowerCase();
    const matchesSearch = searchable.includes(query.toLowerCase());
    const matchesDepartment =
      departmentFilter === "all" ||
      (person.department_name ?? "No department") === departmentFilter;
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" ? person.is_active : !person.is_active);
    const joinedDate = person.created_at.slice(0, 10);
    const matchesRole = roleFilter === "all" || person.role === roleFilter;
    const matchesJoinedFrom = !joinedFrom || joinedDate >= joinedFrom;
    const matchesJoinedTo = !joinedTo || joinedDate <= joinedTo;
    return (
      matchesSearch &&
      matchesDepartment &&
      matchesRole &&
      matchesStatus &&
      matchesJoinedFrom &&
      matchesJoinedTo
    );
  });
  const departments = Array.from(
    new Set(people.map((person) => person.department_name ?? "No department")),
  ).sort();
  const roles = Array.from(new Set(people.map((person) => person.role))).sort();

  function clearFilters() {
    setQuery("");
    setDepartmentFilter("all");
    setRoleFilter("all");
    setStatusFilter("all");
    setJoinedFrom("");
    setJoinedTo("");
  }

  return (
    <div>
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
            Directory
          </p>
          <h1 className="mt-2 font-display text-4xl font-bold tracking-tight sm:text-5xl">
            People
          </h1>
          <p className="mt-3 text-ink/55">
            Everyone employed by or associated with your organization.
          </p>
        </div>
        {canInvite && <InviteMemberDialog />}
      </div>
      <Card className="mt-10 border-0 bg-white">
        <CardContent className="p-4 sm:p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
            <div className="flex min-w-0 flex-1 items-center gap-3 rounded-lg border border-ink/10 px-3 py-2 focus-within:border-coral">
              <Search size={18} className="shrink-0 text-ink/35" />
              <input
                className="w-full min-w-0 bg-transparent text-sm outline-none"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search by name, email, role, or department"
                aria-label="Search people"
              />
            </div>
            {canFilter && (
              <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-ink/45">
                  <Filter size={15} /> Filters
                </div>
                <label className="sr-only" htmlFor="department-filter">
                  Filter by department
                </label>
                <select
                  id="department-filter"
                  value={departmentFilter}
                  onChange={(event) => setDepartmentFilter(event.target.value)}
                  className="h-10 rounded-lg border border-ink/15 bg-white px-3 text-sm outline-none focus:border-coral"
                >
                  <option value="all">All departments</option>
                  {departments.map((department) => (
                    <option key={department} value={department}>
                      {department}
                    </option>
                  ))}
                </select>
                <label className="sr-only" htmlFor="role-filter">
                  Filter by role
                </label>
                <select
                  id="role-filter"
                  value={roleFilter}
                  onChange={(event) => setRoleFilter(event.target.value)}
                  className="h-10 rounded-lg border border-ink/15 bg-white px-3 text-sm outline-none focus:border-coral"
                >
                  <option value="all">All roles</option>
                  {roles.map((role) => (
                    <option key={role} value={role}>
                      {role.replace("_", " ")}
                    </option>
                  ))}
                </select>
                <label className="sr-only" htmlFor="status-filter">
                  Filter by account status
                </label>
                <select
                  id="status-filter"
                  value={statusFilter}
                  onChange={(event) => setStatusFilter(event.target.value)}
                  className="h-10 rounded-lg border border-ink/15 bg-white px-3 text-sm outline-none focus:border-coral"
                >
                  <option value="all">All statuses</option>
                  <option value="active">Active</option>
                  <option value="pending">Pending invite</option>
                </select>
                <label className="sr-only" htmlFor="joined-from">
                  Joined from date
                </label>
                <input
                  id="joined-from"
                  type="date"
                  value={joinedFrom}
                  onChange={(event) => setJoinedFrom(event.target.value)}
                  aria-label="Joined from"
                  className="h-10 rounded-lg border border-ink/15 bg-white px-3 text-sm outline-none focus:border-coral"
                />
                <label className="sr-only" htmlFor="joined-to">
                  Joined to date
                </label>
                <input
                  id="joined-to"
                  type="date"
                  value={joinedTo}
                  onChange={(event) => setJoinedTo(event.target.value)}
                  aria-label="Joined to"
                  className="h-10 rounded-lg border border-ink/15 bg-white px-3 text-sm outline-none focus:border-coral"
                />
                <button
                  type="button"
                  onClick={clearFilters}
                  className="h-10 rounded-lg px-2 text-sm font-semibold text-coral hover:bg-mint"
                >
                  Clear filters
                </button>
              </div>
            )}
          </div>
          <div className="mt-4 flex items-center justify-between text-xs text-ink/45">
            <span>
              {filteredPeople.length} of {people.length} people
            </span>
            {canFilter && <span>HR filters</span>}
          </div>
        </CardContent>
      </Card>
      {error && (
        <Alert className="mt-8" tone="error">
          {error}
        </Alert>
      )}
      <section className="mt-8">
        {loading ? (
          <p className="py-8 text-sm text-ink/55">Loading people...</p>
        ) : filteredPeople.length === 0 ? (
          <div className="py-16 text-center">
            <UserRound className="mx-auto text-coral" size={28} />
            <h2 className="mt-4 font-display text-2xl font-bold">
              No people found
            </h2>
            <p className="mt-2 text-sm text-ink/55">Try a different search.</p>
          </div>
        ) : (
          <Card className="border-0 bg-white">
            <CardContent className="p-4 sm:p-6">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead>Person</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Joined</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPeople.map((person) => (
                    <TableRow key={person.id} className="cursor-pointer">
                      <TableCell>
                        <div className="min-w-48">
                          <p className="font-semibold text-ink">
                            {person.first_name} {person.last_name}
                          </p>
                          <p className="mt-1 break-all text-sm text-ink/55">
                            {person.email}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell className="whitespace-nowrap text-sm text-ink/65">
                        {person.role.replace("_", " ")}
                      </TableCell>
                      <TableCell className="whitespace-nowrap text-sm text-ink/65">
                        {person.department_name ?? "No department"}
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={
                            person.is_active
                              ? "bg-mint text-ink"
                              : "bg-surface text-ink/55"
                          }
                        >
                          {person.is_active ? "Active" : "Pending invite"}
                        </Badge>
                      </TableCell>
                      <TableCell className="whitespace-nowrap text-sm text-ink/55">
                        {new Date(person.created_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  );
}
