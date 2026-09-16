import { LockKeyholeOpen, RefreshCw, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import axios from "axios";
import { authApi } from "../api/auth";
import { Alert, type AlertTone } from "../components/ui/alert";
import { Button } from "../components/ui/button";
import type { LockedUser } from "../types";

export default function AccessControlPage() {
  const [lockedUsers, setLockedUsers] = useState<LockedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [unlockingId, setUnlockingId] = useState<number | null>(null);
  const [feedback, setFeedback] = useState("");
  const [feedbackTone, setFeedbackTone] = useState<AlertTone>("error");

  async function loadLockedUsers() {
    setLoading(true);
    try {
      const { data } = await authApi.listLockedUsers();
      setLockedUsers(data);
      setFeedback("");
    } catch (error) {
      setFeedbackTone("error");
      setFeedback(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadLockedUsers();
  }, []);

  async function unlockUser(lockedUser: LockedUser) {
    setUnlockingId(lockedUser.id);
    setFeedback("");
    try {
      await authApi.unlockUser(lockedUser.id);
      setLockedUsers((current) =>
        current.filter((item) => item.id !== lockedUser.id),
      );
      setFeedbackTone("success");
      setFeedback(
        `${lockedUser.first_name} ${lockedUser.last_name}'s account is unlocked.`,
      );
    } catch (error) {
      setFeedbackTone("error");
      setFeedback(getErrorMessage(error));
    } finally {
      setUnlockingId(null);
    }
  }

  return (
    <div>
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
            Security
          </p>
          <h1 className="mt-2 font-display text-4xl font-bold tracking-tight sm:text-5xl">
            Access Control
          </h1>
          <p className="mt-3 text-ink/55">
            Manage account access and respond to security events across the
            organization.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-coral">
          <ShieldCheck size={17} /> HR & Admin only
        </div>
      </div>
      {feedback && (
        <Alert className="mt-8" tone={feedbackTone}>
          {feedback}
        </Alert>
      )}
      <section className="mt-10 border-t border-ink/10 pt-8">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
              Account security
            </p>
            <h2 className="mt-2 font-display text-2xl font-bold">
              Locked accounts
            </h2>
            <p className="mt-2 text-sm text-ink/55">
              Accounts locked after repeated failed sign-in attempts.
            </p>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={() => void loadLockedUsers()}
            disabled={loading}
            aria-label="Refresh locked accounts"
          >
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
        </div>
        {loading ? (
          <p className="py-8 text-sm text-ink/55">Loading locked accounts...</p>
        ) : lockedUsers.length === 0 ? (
          <div className="py-16 text-center">
            <LockKeyholeOpen className="mx-auto text-coral" size={28} />
            <h3 className="mt-4 font-display text-2xl font-bold">
              No locked accounts
            </h3>
            <p className="mt-2 text-sm text-ink/55">
              Everyone currently has access to their workspace.
            </p>
          </div>
        ) : (
          <div className="mt-6 divide-y divide-ink/10 border-t border-ink/10">
            {lockedUsers.map((lockedUser) => (
              <div
                key={lockedUser.id}
                className="flex flex-col gap-4 py-6 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <h3 className="font-semibold">
                    {lockedUser.first_name} {lockedUser.last_name}
                  </h3>
                  <p className="mt-1 text-sm text-ink/55">
                    {lockedUser.email} · {lockedUser.role.replace("_", " ")}
                  </p>
                  <p className="mt-2 text-xs uppercase tracking-[0.12em] text-ink/40">
                    {lockedUser.failed_login_attempts} failed attempts
                    {lockedUser.locked_at &&
                      ` · Locked ${new Date(lockedUser.locked_at).toLocaleString()}`}
                  </p>
                </div>
                <Button
                  type="button"
                  onClick={() => void unlockUser(lockedUser)}
                  disabled={unlockingId === lockedUser.id}
                >
                  <LockKeyholeOpen size={16} />
                  {unlockingId === lockedUser.id
                    ? "Unlocking..."
                    : "Unlock account"}
                </Button>
              </div>
            ))}
          </div>
        )}
      </section>
      <section className="mt-10 border-t border-ink/10 pt-8">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
          Coming next
        </p>
        <h2 className="mt-2 font-display text-2xl font-bold">
          More security controls
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/55">
          This space is reserved for session controls, sign-in policy, and
          security activity as those capabilities become available.
        </p>
      </section>
    </div>
  );
}

function getErrorMessage(error: unknown) {
  if (
    axios.isAxiosError(error) &&
    typeof error.response?.data?.detail === "string"
  ) {
    return error.response.data.detail;
  }
  return "We could not load the account list. Please try again.";
}
