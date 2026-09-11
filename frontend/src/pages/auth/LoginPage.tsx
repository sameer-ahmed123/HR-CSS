import { useState, type FormEvent } from "react";
import { ArrowRight, LockKeyhole, Mail } from "lucide-react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  if (isAuthenticated) return <Navigate to="/" replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!email || !password) {
      setError("Enter your work email and password.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await login({ email, password });
      navigate(
        (location.state as { from?: { pathname?: string } })?.from?.pathname ??
          "/",
        {
          replace: true,
        },
      );
    } catch {
      setError("We couldn't sign you in with those details.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-ink text-mist lg:grid-cols-[1.1fr_0.9fr]">
      <section className="relative hidden overflow-hidden p-12 lg:flex lg:flex-col lg:justify-between">
        <div className="absolute -right-24 -top-24 h-96 w-96 border-[70px] border-coral/80" />
        <div className="relative">
          <div className="font-display text-2xl font-bold">
            hr<span className="text-coral">.</span>css
          </div>
          <p className="mt-28 max-w-lg font-display text-6xl font-medium leading-[0.98] tracking-tight">
            People operations, with <span className="text-coral">clarity.</span>
          </p>
        </div>
        <div className="relative flex justify-between text-xs uppercase tracking-[0.2em] text-mist/40">
          <span>Human resources / 2026</span>
          <span>Phase 01</span>
        </div>
      </section>
      <section className="flex items-center justify-center bg-surface px-6 py-12 text-ink sm:px-12">
        <div className="w-full max-w-md">
          <div className="mb-12 lg:hidden">
            <div className="font-display text-2xl font-bold">
              hr<span className="text-coral">.</span>css
            </div>
          </div>
          <p className="text-xs font-bold uppercase tracking-[0.22em] text-coral">
            Welcome back
          </p>
          <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">
            Sign in to your workspace
          </h1>
          <p className="mt-3 text-sm text-ink/55">
            Use your corporate account to continue.
          </p>
          <form onSubmit={submit} className="mt-10 space-y-5">
            <Label className="block">
              Work email
              <div className="mt-2 flex items-center gap-3 border-b border-ink/20 py-3 focus-within:border-coral">
                <Mail size={18} className="text-ink/35" />
                <Input
                  className="w-full bg-transparent text-sm outline-none"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  autoComplete="email"
                />
              </div>
            </Label>
            <Label className="block">
              Password
              <div className="mt-2 flex items-center gap-3 border-b border-ink/20 py-3 focus-within:border-coral">
                <LockKeyhole size={18} className="text-ink/35" />
                <Input
                  className="w-full bg-transparent text-sm outline-none"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
              </div>
            </Label>
            {error && (
              <p className="text-sm text-red-700" role="alert">
                {error}
              </p>
            )}
            <Button
              type="submit"
              disabled={submitting}
              className="mt-5 flex w-full items-center justify-center gap-3 bg-coral px-5 py-4 text-sm font-bold transition hover:bg-coral/80 disabled:cursor-wait disabled:opacity-60"
            >
              {submitting ? "Signing in..." : "Continue"}
              <ArrowRight size={18} />
            </Button>
          </form>
          <p className="mt-8 text-center text-sm text-ink/55">
            New to HR-CSS?{" "}
            <Link
              className="font-bold text-ink underline decoration-coral decoration-2 underline-offset-4"
              to="/register"
            >
              Create an account
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
