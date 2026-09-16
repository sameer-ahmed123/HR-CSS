import { Search, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { authApi } from "../api/auth";
import { Alert } from "../components/ui/alert";
import InviteMemberDialog from "../components/organization/InviteMemberDialog";
import { useAuth } from "../context/AuthContext";
import type { OrganizationUser } from "../types";

export default function PeoplePage() {
  const { user } = useAuth();
  const [people, setPeople] = useState<OrganizationUser[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const canInvite = user?.role === "ADMIN" || user?.role === "HR";

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
    return searchable.includes(query.toLowerCase());
  });

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
      <div className="mt-10 flex items-center gap-3 border-b border-ink/15 py-3 focus-within:border-coral">
        <Search size={18} className="text-ink/35" />
        <input
          className="w-full bg-transparent text-sm outline-none"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search by name, email, role, or department"
          aria-label="Search people"
        />
      </div>
      {error && (
        <Alert className="mt-8" tone="error">
          {error}
        </Alert>
      )}
      <section className="mt-8 border-t border-ink/10">
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
          <div className="divide-y divide-ink/10">
            {filteredPeople.map((person) => (
              <div
                key={person.id}
                className="flex flex-col gap-3 py-5 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <h2 className="font-semibold">
                    {person.first_name} {person.last_name}
                  </h2>
                  <p className="mt-1 text-sm text-ink/55">{person.email}</p>
                </div>
                <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs uppercase tracking-[0.12em] text-ink/45 sm:text-right">
                  <span>{person.role.replace("_", " ")}</span>
                  <span>{person.department_name ?? "No department"}</span>
                  <span
                    className={person.is_active ? "text-coral" : "text-ink/40"}
                  >
                    {person.is_active ? "Active" : "Pending invite"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
