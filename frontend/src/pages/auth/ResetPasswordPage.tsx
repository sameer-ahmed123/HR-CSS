import { useEffect, useState, type FormEvent } from "react";
import { ArrowRight, LockKeyhole } from "lucide-react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { authApi } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { AuthShell } from "./ForgotPasswordPage";
import { Alert } from "../../components/ui/alert";

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const navigate = useNavigate();
  const { setSession } = useAuth();
  const [valid, setValid] = useState<boolean | null>(null);
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    async function verifyResetToken() {
      if (!token) {
        setValid(false);
        return;
      }
      try {
        await authApi.verifyPasswordReset(token);
        setValid(true);
      } catch {
        setValid(false);
      }
    }
    void verifyResetToken();
  }, [token]);
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
      const { data } = await authApi.confirmPasswordReset(
        token,
        password,
        confirmation,
      );
      setSession(data);
      navigate("/home", { replace: true });
    } catch {
      setError("This reset link is invalid or expired.");
    } finally {
      setSubmitting(false);
    }
  }
  return (
    <AuthShell
      eyebrow="Account recovery"
      title="Set a new password"
      subtitle={
        valid
          ? "Choose a strong password for your HR-CSS account."
          : "Checking your secure reset link..."
      }
    >
      {valid ? (
        <form onSubmit={submit} className="mt-8 space-y-5">
          <PasswordField
            label="New password"
            value={password}
            onChange={setPassword}
          />
          <PasswordField
            label="Confirm password"
            value={confirmation}
            onChange={setConfirmation}
          />
          {error && <Alert tone="error">{error}</Alert>}
          <Button disabled={submitting} className="w-full bg-coral px-5 py-4">
            {submitting ? "Updating..." : "Update password"}
            <ArrowRight size={18} />
          </Button>
        </form>
      ) : valid === false ? (
        <div className="mt-7">
          <Alert tone="error">This reset link is invalid or expired.</Alert>
          <Link
            className="mt-6 inline-block text-sm font-bold underline decoration-coral decoration-2 underline-offset-4"
            to="/forgot-password"
          >
            Request a new link
          </Link>
        </div>
      ) : (
        <p className="mt-7 text-sm text-ink/55">Please wait...</p>
      )}
    </AuthShell>
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
