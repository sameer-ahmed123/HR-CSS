import { useState, type FormEvent } from "react";
import { ArrowRight, Mail } from "lucide-react";
import { Link } from "react-router-dom";
import { authApi } from "../../api/auth";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Alert } from "../../components/ui/alert";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setMessage("");
    setError("");
    try {
      const { data } = await authApi.requestPasswordReset(email);
      setMessage(data.detail);
    } catch {
      setError("We could not process that request. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Account recovery"
      title="Forgot your password?"
      subtitle="Enter your work email and we will send you a secure reset link."
    >
      <form onSubmit={submit} className="mt-8 space-y-5">
        <Label className="block">
          Work email
          <div className="mt-2 flex items-center gap-3 border-b border-ink/20 py-3 focus-within:border-coral">
            <Mail size={18} className="text-ink/35" />
            <Input
              className="w-full"
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@company.com"
            />
          </div>
        </Label>
        {message && <Alert tone="success">{message}</Alert>}
        {error && <Alert tone="error">{error}</Alert>}
        <Button disabled={submitting} className="w-full bg-coral px-5 py-4">
          {submitting ? "Sending..." : "Send reset link"}
          <ArrowRight size={18} />
        </Button>
      </form>
      <p className="mt-7 text-center text-sm text-ink/55">
        <Link
          className="font-bold underline decoration-coral decoration-2 underline-offset-4"
          to="/login"
        >
          Return to sign in
        </Link>
      </p>
    </AuthShell>
  );
}

export function AuthShell({
  eyebrow,
  title,
  subtitle,
  children,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-surface px-6 py-12 text-ink">
      <div className="w-full max-w-md rounded-3xl border border-ink/10 bg-white p-8 shadow-sm">
        <div className="font-display text-2xl font-bold">
          hr<span className="text-coral">.</span>css
        </div>
        <p className="mt-12 text-xs font-bold uppercase tracking-[0.16em] text-coral">
          {eyebrow}
        </p>
        <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">
          {title}
        </h1>
        <p className="mt-3 text-sm text-ink/55">{subtitle}</p>
        {children}
      </div>
    </main>
  );
}
