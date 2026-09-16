import { useEffect, useState, type FormEvent } from "react";
import { ArrowRight, LockKeyhole } from "lucide-react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { authApi } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import type { InviteVerification } from "../../types";
import { Alert } from "../../components/ui/alert";

export default function AcceptInvitePage() {
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get("token") ?? "";
  const { acceptInvite, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [invite, setInvite] = useState<InviteVerification | null>(null);
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function verifyInvitation() {
      if (!inviteToken) {
        setError("This invitation link is missing its token.");
        setLoading(false);
        return;
      }
      try {
        const { data } = await authApi.verifyInvite(inviteToken);
        setInvite(data);
      } catch {
        setError("This invitation is invalid or has expired.");
      } finally {
        setLoading(false);
      }
    }
    void verifyInvitation();
  }, [inviteToken]);

  if (isAuthenticated) return <Navigate to="/home" replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (password.length < 8) {
      setError("Your password must be at least 8 characters.");
      return;
    }
    if (password !== confirmation) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await acceptInvite(inviteToken, password);
      navigate("/home", { replace: true });
    } catch {
      setError(
        "We could not activate this invitation. Please request a new link.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-surface px-6 py-12 text-ink">
      <div className="w-full max-w-md rounded-3xl border border-ink/10 bg-white p-8 shadow-sm">
        <Link to="/login" className="font-display text-2xl font-bold">
          hr<span className="text-coral">.</span>css
        </Link>
        <p className="mt-12 text-xs font-bold uppercase tracking-[0.16em] text-coral">
          Finish setting up
        </p>
        <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">
          Set your password
        </h1>
        {loading ? (
          <p className="mt-4 text-sm text-ink/55">
            Checking your invitation...
          </p>
        ) : invite ? (
          <>
            <p className="mt-3 text-sm text-ink/55">
              Welcome, {invite.first_name}. Your account will be created for{" "}
              {invite.email}.
            </p>
            <form onSubmit={submit} className="mt-8 space-y-5">
              <PasswordField
                label="Password"
                value={password}
                onChange={setPassword}
              />
              <PasswordField
                label="Confirm password"
                value={confirmation}
                onChange={setConfirmation}
              />
              {error && <Alert tone="error">{error}</Alert>}
              <Button
                type="submit"
                disabled={submitting}
                className="mt-3 w-full bg-coral px-5 py-4"
              >
                {submitting ? "Activating account..." : "Activate account"}
                <ArrowRight size={18} />
              </Button>
            </form>
          </>
        ) : (
          <div className="mt-6">
            <Alert tone="error">{error}</Alert>
            <Link
              to="/login"
              className="mt-6 inline-block text-sm font-bold underline decoration-coral decoration-2 underline-offset-4"
            >
              Return to sign in
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}

function PasswordField({
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
      <div className="mt-2 flex items-center gap-3 border-b border-ink/20 py-3 focus-within:border-coral">
        <LockKeyhole size={18} className="text-ink/35" />
        <Input
          className="w-full"
          type="password"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          autoComplete="new-password"
        />
      </div>
    </Label>
  );
}
