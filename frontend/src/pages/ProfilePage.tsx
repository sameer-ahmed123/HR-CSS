import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { KeyRound, RefreshCw, ShieldCheck, UserRound } from "lucide-react";
import { authApi } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import type { LoginHistory, SentInvite } from "../types";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Alert, type AlertTone } from "../components/ui/alert";

export default function ProfilePage() {
  const { user, logoutAll } = useAuth();
  const [tab, setTab] = useState<"overview" | "activity" | "invites">(
    "overview",
  );
  const [history, setHistory] = useState<LoginHistory[]>([]);
  const [invites, setInvites] = useState<SentInvite[]>([]);
  const [message, setMessage] = useState<{
    text: string;
    tone: AlertTone;
  } | null>(null);
  const canViewInvites = user?.role === "ADMIN" || user?.role === "HR";

  useEffect(() => {
    async function loadProfileData() {
      try {
        const { data } = await authApi.loginHistory();
        setHistory(data);
      } catch {
        setHistory([]);
      }
      if (canViewInvites) {
        try {
          const { data } = await authApi.myInvites();
          setInvites(data);
        } catch {
          setInvites([]);
        }
      }
    }
    void loadProfileData();
  }, [canViewInvites]);

  async function resend(userId: number) {
    try {
      await authApi.resendInvite(userId);
      setMessage({ text: "Invitation resent successfully.", tone: "success" });
    } catch {
      setMessage({
        text: "We could not resend that invitation.",
        tone: "error",
      });
    }
  }

  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
            Your account
          </p>
          <h1 className="mt-2 font-display text-4xl font-bold tracking-tight">
            Profile & security
          </h1>
          <p className="mt-3 text-ink/55">
            Manage your profile, password, and account activity.
          </p>
        </div>
        <Button variant="outline" onClick={logoutAll}>
          <ShieldCheck size={17} /> Sign out everywhere
        </Button>
      </div>
      <div className="mt-8 flex gap-2 border-b border-ink/10">
        <Tab active={tab === "overview"} onClick={() => setTab("overview")}>
          Overview
        </Tab>
        <Tab active={tab === "activity"} onClick={() => setTab("activity")}>
          Login activity
        </Tab>
        {canViewInvites && (
          <Tab active={tab === "invites"} onClick={() => setTab("invites")}>
            Sent invites
          </Tab>
        )}
      </div>
      {message && (
        <Alert className="mt-4" tone={message.tone}>
          {message.text}
        </Alert>
      )}
      {tab === "overview" && (
        <Overview
          user={user}
          onMessage={(text, tone) => setMessage({ text, tone })}
        />
      )}
      {tab === "activity" && <Activity history={history} />}
      {tab === "invites" && <Invites invites={invites} onResend={resend} />}
    </div>
  );
}

function Tab({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`border-b-2 px-3 py-3 text-sm font-semibold transition ${active ? "border-coral text-ink" : "border-transparent text-ink/45 hover:text-ink"}`}
    >
      {children}
    </button>
  );
}

function Overview({
  user,
  onMessage,
}: {
  user: ReturnType<typeof useAuth>["user"];
  onMessage: (message: string, tone: AlertTone) => void;
}) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [saving, setSaving] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      await authApi.changePassword(oldPassword, newPassword, confirmation);
      setOldPassword("");
      setNewPassword("");
      setConfirmation("");
      onMessage(
        "Password changed successfully. Other sessions were signed out.",
        "success",
      );
    } catch {
      onMessage(
        "The current password was incorrect or the new passwords did not match.",
        "error",
      );
    } finally {
      setSaving(false);
    }
  }
  return (
    <div className="mt-6 grid gap-5 lg:grid-cols-[1fr_1fr]">
      <Card className="border-0 bg-white">
        <CardContent>
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-mint">
              <UserRound size={18} />
            </span>
            <div>
              <h2 className="font-display text-xl font-bold">
                Personal details
              </h2>
              <p className="text-sm text-ink/50">Your HR-CSS profile</p>
            </div>
          </div>
          <dl className="mt-8 space-y-4 text-sm">
            <Detail
              label="Name"
              value={`${user?.first_name ?? ""} ${user?.last_name ?? ""}`}
            />
            <Detail label="Email" value={user?.email ?? ""} />
            <Detail label="Role" value={user?.role ?? ""} />
            <Detail
              label="Joined"
              value={
                user?.created_at
                  ? new Date(user.created_at).toLocaleDateString()
                  : "-"
              }
            />
          </dl>
        </CardContent>
      </Card>
      <Card className="border-0 bg-white">
        <CardContent>
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-mint">
              <KeyRound size={18} />
            </span>
            <div>
              <h2 className="font-display text-xl font-bold">
                Change password
              </h2>
              <p className="text-sm text-ink/50">Keep your account protected</p>
            </div>
          </div>
          <form onSubmit={submit} className="mt-8 space-y-4">
            <PasswordInput
              label="Current password"
              value={oldPassword}
              onChange={setOldPassword}
            />
            <PasswordInput
              label="New password"
              value={newPassword}
              onChange={setNewPassword}
            />
            <PasswordInput
              label="Confirm new password"
              value={confirmation}
              onChange={setConfirmation}
            />
            <Button disabled={saving} className="w-full">
              {saving ? "Updating..." : "Change password"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-ink/10 pb-3">
      <dt className="text-ink/50">{label}</dt>
      <dd className="text-right font-semibold">{value}</dd>
    </div>
  );
}

function PasswordInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <Label className="block">
      {label}
      <Input
        className="mt-2 border border-ink/15 px-3"
        type="password"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </Label>
  );
}

function Activity({ history }: { history: LoginHistory[] }) {
  return (
    <Card className="mt-6 border-0 bg-white">
      <CardContent>
        <h2 className="font-display text-xl font-bold">
          Recent login activity
        </h2>
        <div className="mt-5 divide-y divide-ink/10">
          {history.length ? (
            history.map((item) => (
              <div
                key={item.id}
                className="flex flex-col justify-between gap-2 py-4 text-sm sm:flex-row"
              >
                <div>
                  <Badge
                    className={`rounded-full ${item.status === "SUCCESS" ? "bg-mint text-ink" : "bg-red-100 text-red-700"}`}
                  >
                    {item.status}
                  </Badge>
                  <span className="ml-3 text-ink/55">
                    {item.ip_address ?? "Unknown IP"}
                  </span>
                </div>
                <span className="text-ink/45">
                  {new Date(item.timestamp).toLocaleString()}
                </span>
              </div>
            ))
          ) : (
            <p className="py-6 text-sm text-ink/55">No login activity yet.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function Invites({
  invites,
  onResend,
}: {
  invites: SentInvite[];
  onResend: (userId: number) => void;
}) {
  return (
    <Card className="mt-6 border-0 bg-white">
      <CardContent>
        <h2 className="font-display text-xl font-bold">Invitations you sent</h2>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[600px] text-left text-sm">
            <thead className="border-b border-ink/10 text-xs uppercase tracking-wider text-ink/45">
              <tr>
                <th className="px-3 py-3">Email</th>
                <th className="px-3 py-3">Role</th>
                <th className="px-3 py-3">Status</th>
                <th className="px-3 py-3">Sent</th>
                <th className="px-3 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-ink/10">
              {invites.map((invite) => (
                <tr key={invite.user_id}>
                  <td className="px-3 py-4 font-semibold">{invite.email}</td>
                  <td className="px-3 py-4">{invite.role}</td>
                  <td className="px-3 py-4">
                    <Badge
                      className={`rounded-full ${invite.status === "Activated" ? "bg-mint text-ink" : "bg-amber-100 text-amber-800"}`}
                    >
                      {invite.status}
                    </Badge>
                  </td>
                  <td className="px-3 py-4 text-ink/55">
                    {new Date(invite.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-3 py-4">
                    {invite.status === "Pending" && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onResend(invite.user_id)}
                        aria-label={`Resend invite to ${invite.email}`}
                      >
                        <RefreshCw size={16} />
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!invites.length && (
            <p className="py-6 text-sm text-ink/55">No invitations sent yet.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
