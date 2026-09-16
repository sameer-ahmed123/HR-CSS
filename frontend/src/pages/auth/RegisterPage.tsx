import { useState, type FormEvent } from "react";
import { ArrowRight, LockKeyhole, Mail, Phone, UserRound } from "lucide-react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";

export default function RegisterPage() {
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    password: "",
    password_confirmation: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  function updateField(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (Object.values(form).some((value) => !value)) {
      setError("Complete all fields to create your account.");
      return;
    }
    if (form.password.length < 8) {
      setError("Your password must be at least 8 characters.");
      return;
    }
    if (form.password !== form.password_confirmation) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await register(form);
      navigate("/", { replace: true });
    } catch {
      setError(
        "We couldn't create your account. The email may already be registered.",
      );
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
            Your people, your <span className="text-coral">place.</span>
          </p>
        </div>
        <div className="relative flex justify-between text-xs uppercase tracking-[0.2em] text-mist/40">
          <span>Human resources / 2026</span>
          <span>Phase 01</span>
        </div>
      </section>
      <section className="flex items-center justify-center bg-white px-6 py-10 text-ink sm:px-12">
        <div className="w-full max-w-md rounded-3xl border border-ink/10 bg-white p-2 sm:p-6">
          <div className="mb-10 lg:hidden">
            <div className="font-display text-2xl font-bold">
              hr<span className="text-coral">.</span>css
            </div>
          </div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
            Create your account
          </p>
          <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">
            Join your workspace
          </h1>
          <p className="mt-3 text-sm text-ink/55">
            New accounts start with employee access.
          </p>
          <form onSubmit={submit} className="mt-8 space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field
                label="First name"
                icon={<UserRound size={17} />}
                value={form.first_name}
                onChange={(value) => updateField("first_name", value)}
                autoComplete="given-name"
              />
              <Field
                label="Last name"
                icon={<UserRound size={17} />}
                value={form.last_name}
                onChange={(value) => updateField("last_name", value)}
                autoComplete="family-name"
              />
            </div>
            <Field
              label="Work email"
              icon={<Mail size={17} />}
              type="email"
              value={form.email}
              onChange={(value) => updateField("email", value)}
              autoComplete="email"
            />
            <Field
              label="Phone number"
              icon={<Phone size={17} />}
              type="tel"
              value={form.phone_number}
              onChange={(value) => updateField("phone_number", value)}
              autoComplete="tel"
            />
            <Field
              label="Password"
              icon={<LockKeyhole size={17} />}
              type="password"
              value={form.password}
              onChange={(value) => updateField("password", value)}
              autoComplete="new-password"
            />
            <Field
              label="Confirm password"
              icon={<LockKeyhole size={17} />}
              type="password"
              value={form.password_confirmation}
              onChange={(value) => updateField("password_confirmation", value)}
              autoComplete="new-password"
            />
            {error && (
              <p className="text-sm text-red-700" role="alert">
                {error}
              </p>
            )}
            <Button
              type="submit"
              disabled={submitting}
              className="mt-3 flex w-full items-center justify-center gap-3 bg-coral px-5 py-4 text-sm font-bold transition hover:bg-coral/80 disabled:cursor-wait disabled:opacity-60"
            >
              {submitting ? "Creating account..." : "Create account"}
              <ArrowRight size={18} />
            </Button>
          </form>
          <p className="mt-7 text-center text-sm text-ink/55">
            Already have an account?{" "}
            <Link
              className="font-bold text-ink underline decoration-coral decoration-2 underline-offset-4"
              to="/login"
            >
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

function Field({
  label,
  icon,
  value,
  onChange,
  type = "text",
  autoComplete,
}: {
  label: string;
  icon: React.ReactNode;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  autoComplete?: string;
}) {
  return (
    <Label className="block">
      {label}
      <div className="mt-1 flex items-center gap-3 border-b border-ink/20 py-2.5 focus-within:border-coral">
        <span className="text-ink/35">{icon}</span>
        <Input
          className="w-full bg-transparent text-sm outline-none"
          type={type}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          autoComplete={autoComplete}
        />
      </div>
    </Label>
  );
}
