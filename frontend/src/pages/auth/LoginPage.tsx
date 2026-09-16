import { useState } from "react";
import axios from "axios";
import { ArrowRight, LockKeyhole, Mail } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Alert } from "../../components/ui/alert";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<{ email: string; password: string }>();
  if (isAuthenticated) return <Navigate to="/home" replace />;

  async function submit(credentials: { email: string; password: string }) {
    setSubmitting(true);
    setError("");
    try {
      await login(credentials);
      navigate(
        (location.state as { from?: { pathname?: string } })?.from?.pathname ??
          "/home",
        {
          replace: true,
        },
      );
    } catch (error) {
      setError(getLoginErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-surface text-ink lg:grid-cols-[1.05fr_0.95fr]">
      <section className="relative hidden overflow-hidden bg-ink p-12 text-mist lg:flex lg:flex-col lg:justify-between">
        <div className="absolute -right-24 -top-24 h-96 w-96 rounded-full border-[70px] border-coral/30" />
        <div className="relative">
          <div className="font-display text-2xl font-bold">
            hr<span className="text-coral">.</span>css
          </div>
          <p className="mt-28 max-w-lg font-display text-6xl font-bold leading-[1.02] tracking-tight">
            A better day at work starts{" "}
            <span className="text-coral">here.</span>
          </p>
        </div>
        <div className="relative flex justify-between text-xs uppercase tracking-[0.2em] text-mist/40">
          <span>Human resources / 2026</span>
          <span>Phase 01</span>
        </div>
      </section>
      <section className="flex items-center justify-center bg-white px-6 py-12 text-ink sm:px-12">
        <div className="w-full max-w-md rounded-3xl border border-ink/10 bg-white p-2 sm:p-6">
          <div className="mb-12 lg:hidden">
            <div className="font-display text-2xl font-bold">
              hr<span className="text-coral">.</span>css
            </div>
          </div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
            Welcome back
          </p>
          <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">
            Sign in to your workspace
          </h1>
          <p className="mt-3 text-sm text-ink/55">
            Use your corporate account to continue.
          </p>
          <form onSubmit={handleSubmit(submit)} className="mt-10 space-y-5">
            <Label className="block">
              Work email
              <div className="mt-2 flex items-center gap-3 border-b border-ink/20 py-3 focus-within:border-coral">
                <Mail size={18} className="text-ink/35" />
                <Input
                  className="w-full bg-transparent text-sm outline-none"
                  type="email"
                  {...register("email", {
                    required: "Enter your work email.",
                    pattern: {
                      value: /\S+@\S+\.\S+/,
                      message: "Enter a valid email.",
                    },
                  })}
                  placeholder="you@company.com"
                  autoComplete="email"
                />
              </div>
              {errors.email && (
                <span className="mt-1 block text-xs font-normal text-red-700">
                  {errors.email.message}
                </span>
              )}
            </Label>
            <Label className="block">
              Password
              <div className="mt-2 flex items-center gap-3 border-b border-ink/20 py-3 focus-within:border-coral">
                <LockKeyhole size={18} className="text-ink/35" />
                <Input
                  className="w-full bg-transparent text-sm outline-none"
                  type="password"
                  {...register("password", {
                    required: "Enter your password.",
                  })}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
              </div>
              {errors.password && (
                <span className="mt-1 block text-xs font-normal text-red-700">
                  {errors.password.message}
                </span>
              )}
            </Label>
            {error && <Alert tone="error">{error}</Alert>}
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
          <p className="mt-3 text-center text-sm">
            <Link
              className="text-ink/55 underline decoration-coral underline-offset-4"
              to="/forgot-password"
            >
              Forgot your password?
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

function getLoginErrorMessage(error: unknown) {
  if (!axios.isAxiosError(error))
    return "We couldn't sign you in with those details.";
  const data = error.response?.data as Record<string, unknown> | undefined;
  if (typeof data?.detail === "string") return data.detail;
  for (const value of Object.values(data ?? {})) {
    if (Array.isArray(value) && typeof value[0] === "string") return value[0];
    if (typeof value === "string") return value;
  }
  return "We couldn't sign you in with those details.";
}
