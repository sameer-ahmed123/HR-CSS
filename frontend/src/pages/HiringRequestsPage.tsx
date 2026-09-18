import { Plus, Trash2 } from "lucide-react";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { recruitmentApi } from "../api/recruitment";
import { organizationApi } from "../api/organization";
import { Alert } from "../components/ui/alert";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import type {
  Department,
  HiringRequest,
  HiringRequestInput,
  HiringRequestUrgency,
} from "../types";

const urgencyOptions: HiringRequestUrgency[] = [
  "LOW",
  "MEDIUM",
  "HIGH",
  "URGENT",
];

export default function HiringRequestsPage() {
  const [requests, setRequests] = useState<HiringRequest[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState<HiringRequestInput>({
    request_title: "",
    department: 0,
    headcount: 1,
    seniority: "",
    budget: "",
    reason: "",
    urgency: "MEDIUM",
    required_experience: "",
    required_qualifications: "",
  });

  useEffect(() => {
    async function load() {
      try {
        const [{ data: requestData }, { data: departmentData }] =
          await Promise.all([
            recruitmentApi.listHiringRequests(),
            organizationApi.listDepartments(),
          ]);
        setRequests(requestData);
        setDepartments(departmentData);
      } catch {
        setError("We could not load hiring requests. Please try again.");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (
      !form.request_title.trim() ||
      form.department < 1 ||
      form.headcount < 1 ||
      !form.seniority.trim() ||
      !form.reason.trim() ||
      !form.required_experience.trim() ||
      !form.required_qualifications.trim()
    ) {
      setError("Complete the required fields before submitting this request.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const { data } = await recruitmentApi.createHiringRequest({
        ...form,
        request_title: form.request_title.trim(),
        budget: form.budget?.trim() || null,
      });
      setRequests((current) => [data, ...current]);
      setForm({
        request_title: "",
        department: 0,
        headcount: 1,
        seniority: "",
        budget: "",
        reason: "",
        urgency: "MEDIUM",
        required_experience: "",
        required_qualifications: "",
      });
    } catch {
      setError("We could not submit this hiring request.");
    } finally {
      setSaving(false);
    }
  }

  async function removeRequest(id: number) {
    try {
      await recruitmentApi.deleteHiringRequest(id);
      setRequests((current) => current.filter((request) => request.id !== id));
    } catch {
      setError("Only pending requests can be deleted.");
    }
  }

  return (
    <div>
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
          Workforce planning
        </p>
        <h1 className="mt-2 font-display text-4xl font-bold tracking-tight sm:text-5xl">
          Hiring requests
        </h1>
        <p className="mt-3 max-w-2xl text-ink/55">
          Request the headcount your department needs and keep the approval
          queue clear.
        </p>
      </div>
      {error && (
        <Alert className="mt-8" tone="error">
          {error}
        </Alert>
      )}

      <div className="mt-10 grid min-w-0 gap-8 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <Card className="min-w-0 border-0 bg-ink text-mist">
          <CardContent>
            <div className="flex items-start gap-3">
              <span className="grid h-10 w-10 place-items-center bg-coral text-ink">
                <Plus size={19} />
              </span>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
                  New request
                </p>
                <h2 className="mt-1 font-display text-2xl font-bold">
                  Build the case
                </h2>
                <p className="mt-1 text-sm leading-5 text-mist/55">
                  Required fields are marked with an asterisk.
                </p>
              </div>
            </div>
            <form onSubmit={submit} className="mt-8 space-y-6">
              <Field label="Request title" required>
                <Input
                  required
                  value={form.request_title}
                  onChange={(event) =>
                    setForm({ ...form, request_title: event.target.value })
                  }
                  placeholder="Senior product designer"
                  className="border-white/15 bg-white/10 text-mist placeholder:text-mist/40"
                />
              </Field>
              <Field label="Department" required>
                <select
                  required
                  value={form.department || ""}
                  onChange={(event) =>
                    setForm({ ...form, department: Number(event.target.value) })
                  }
                  className="mt-2 h-10 w-full rounded-lg border border-white/15 bg-white/10 px-3 text-sm text-mist"
                >
                  <option value="" className="text-ink">
                    Select department
                  </option>
                  {departments.map((department) => (
                    <option
                      key={department.id}
                      value={department.id}
                      className="text-ink"
                    >
                      {department.name}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Seniority" required>
                <Input
                  required
                  value={form.seniority}
                  onChange={(event) =>
                    setForm({ ...form, seniority: event.target.value })
                  }
                  placeholder="Mid-level"
                  className="border-white/15 bg-white/10 text-mist placeholder:text-mist/40"
                />
              </Field>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Headcount" required>
                  <Input
                    required
                    type="number"
                    min={1}
                    value={form.headcount}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        headcount: Number(event.target.value),
                      })
                    }
                    className="border-white/15 bg-white/10 text-mist"
                  />
                </Field>
                <Field label="Urgency">
                  <select
                    value={form.urgency}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        urgency: event.target.value as HiringRequestUrgency,
                      })
                    }
                    className="mt-2 h-10 w-full rounded-lg border border-white/15 bg-white/10 px-3 text-sm text-mist"
                  >
                    {urgencyOptions.map((urgency) => (
                      <option
                        key={urgency}
                        value={urgency}
                        className="text-ink"
                      >
                        {urgency}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
              <Field label="Budget">
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  value={form.budget ?? ""}
                  onChange={(event) =>
                    setForm({ ...form, budget: event.target.value })
                  }
                  placeholder="Optional budget"
                  className="border-white/15 bg-white/10 text-mist placeholder:text-mist/40"
                />
              </Field>
              <Field label="Reason for request" required>
                <textarea
                  required
                  value={form.reason}
                  onChange={(event) =>
                    setForm({ ...form, reason: event.target.value })
                  }
                  rows={3}
                  className="mt-2 min-h-24 w-full resize-y rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-mist outline-none placeholder:text-mist/40 focus:border-coral"
                  placeholder="Why is this role needed?"
                />
              </Field>
              <Field label="Required experience" required>
                <Input
                  required
                  value={form.required_experience}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      required_experience: event.target.value,
                    })
                  }
                  placeholder="Relevant experience"
                  className="border-white/15 bg-white/10 text-mist placeholder:text-mist/40"
                />
              </Field>
              <Field label="Required qualifications" required>
                <textarea
                  required
                  value={form.required_qualifications}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      required_qualifications: event.target.value,
                    })
                  }
                  rows={3}
                  className="mt-2 min-h-24 w-full resize-y rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-mist outline-none placeholder:text-mist/40 focus:border-coral"
                  placeholder="Qualifications and certifications"
                />
              </Field>
              <Button
                type="submit"
                disabled={saving}
                className="w-full bg-coral text-ink hover:bg-coral/90"
              >
                {saving ? "Submitting..." : "Submit request"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <section className="min-w-0">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
                Your queue
              </p>
              <h2 className="mt-2 font-display text-2xl font-bold">
                Submitted requests
              </h2>
            </div>
            <span className="text-sm text-ink/45">{requests.length} total</span>
          </div>
          {loading ? (
            <p className="py-8 text-sm text-ink/55">Loading requests...</p>
          ) : (
            <div className="mt-5 divide-y divide-ink/10 border-y border-ink/10">
              {requests.length === 0 ? (
                <p className="py-8 text-sm text-ink/55">
                  No hiring requests yet.
                </p>
              ) : (
                requests.map((request) => (
                  <div
                    key={request.id}
                    className="flex flex-col gap-4 py-5 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <h3 className="break-words font-display text-xl font-bold">
                        {request.request_title}
                      </h3>
                      <p className="mt-1 text-sm text-ink/55">
                        {departmentName(request.department, departments)} ·{" "}
                        {request.headcount} hire
                        {request.headcount === 1 ? "" : "s"}
                      </p>
                      <p className="mt-2 text-xs uppercase tracking-[0.12em] text-ink/40">
                        Created{" "}
                        {new Date(request.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge
                        className={
                          request.status === "REJECTED"
                            ? "bg-coral text-ink"
                            : "bg-mint text-ink"
                        }
                      >
                        {request.status}
                      </Badge>
                      {request.status === "PENDING" && (
                        <button
                          type="button"
                          onClick={() => void removeRequest(request.id)}
                          aria-label={`Delete ${request.request_title}`}
                          className="rounded-lg p-2 text-ink/45 hover:bg-surface hover:text-ink"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function Field({
  label,
  required = false,
  children,
}: {
  label: string;
  required?: boolean;
  children: ReactNode;
}) {
  return (
    <Label className="block text-mist/75">
      {label}
      {required && (
        <span className="ml-1 text-coral" aria-hidden="true">
          *
        </span>
      )}
      {children}
    </Label>
  );
}

function departmentName(id: number, departments: Department[]) {
  return (
    departments.find((department) => department.id === id)?.name ??
    "Unknown department"
  );
}
