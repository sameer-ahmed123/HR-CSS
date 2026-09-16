import { ArrowUpRight, Clock3, UsersRound } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { useAuth } from "../context/AuthContext";
import InviteMemberDialog from "../components/organization/InviteMemberDialog";

export default function DashboardPage() {
  const { user } = useAuth();
  const canInvite = user?.role === "ADMIN" || user?.role === "HR";
  return (
    <div>
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
            Monday, 11 September 2026 · Your workspace
          </p>
          <h1 className="mt-2 font-display text-4xl font-bold tracking-tight sm:text-5xl">
            Good morning, team.
          </h1>
          <p className="mt-3 text-ink/55">
            Here is a quick look at what is happening across your organization.
          </p>
        </div>
        <div className="flex flex-wrap gap-3 self-start">
          <Button variant="outline">
            View reports <ArrowUpRight size={16} />
          </Button>
          {canInvite && <InviteMemberDialog />}
        </div>
      </div>
      <div className="mt-10 grid gap-4 md:grid-cols-3">
        <Card className="border-0 bg-white">
          <CardContent>
            <div className="flex items-center justify-between">
              <UsersRound className="text-coral" size={22} />
              <Badge className="rounded-full bg-mint text-ink">Live</Badge>
            </div>
            <p className="mt-10 text-sm text-ink/55">Active people</p>
            <p className="mt-1 font-display text-4xl font-bold">248</p>
          </CardContent>
        </Card>
        <Card className="border-0 bg-white">
          <CardContent>
            <Clock3 className="text-coral" size={22} />
            <p className="mt-10 text-sm text-ink/55">Pending requests</p>
            <p className="mt-1 font-display text-4xl font-bold">12</p>
            <Badge className="mt-4 rounded-full bg-surface text-ink/55">
              Needs review
            </Badge>
          </CardContent>
        </Card>
        <Card className="border-0 bg-mint">
          <CardContent>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-ink/55">
              Organization health
            </p>
            <p className="mt-9 font-display text-4xl font-bold">
              92<span className="text-xl">%</span>
            </p>
            <p className="mt-2 text-sm text-ink/55">Up 4.6% this month</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
