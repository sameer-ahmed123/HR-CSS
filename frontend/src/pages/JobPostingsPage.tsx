import { Eye, PencilLine, Plus, Trash2 } from "lucide-react";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { recruitmentApi } from "../api/recruitment";
import { organizationApi } from "../api/organization";
import { Alert } from "../components/ui/alert";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { useAuth } from "../context/AuthContext";
import type {
  Department,
  HiringRequest,
  JobPosting,
  JobPostingInput,
  JobStatus,
} from "../types";

const emptyForm = {
  job_title: "",
  job_description: "",
  department: 0,
  hiring_request: null,
  required_skills: "",
  required_experience: "",
  closing_date: "",
  cv_score_threshold: 70,
  status: "DRAFT" as JobStatus,
};

export default function JobPostingsPage() {
  const { user } = useAuth();
  const canManage =
    user?.role === "ADMIN" || user?.role === "HR" || user?.role === "TEAM_LEAD";
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [requests, setRequests] = useState<HiringRequest[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState<JobPostingInput>(emptyForm);

  useEffect(() => {
    async function load() {
      try {
        const [
          { data: postings },
          { data: hiringRequests },
          { data: departmentData },
        ] = await Promise.all([
          recruitmentApi.listJobPostings(),
          recruitmentApi.listHiringRequests(),
          organizationApi.listDepartments(),
        ]);
        setJobPostings(postings);
        setRequests(hiringRequests);
        setDepartments(departmentData);
        if (user?.department && !canManage) {
          setForm((current) => ({
            ...current,
            department: user.department ?? 0,
          }));
        }
      } catch {
        setError("We could not load job postings.");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [canManage, user?.department]);

  const approvedHiringRequests = requests.filter(
    (request) => request.status === "APPROVED",
  );

  function resetForm() {
    setForm({
      ...emptyForm,
      department: canManage ? 0 : (user?.department ?? 0),
    });
    setEditingId(null);
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (
      !form.job_title.trim() ||
      !form.job_description.trim() ||
      !form.required_skills.trim() ||
      !form.required_experience.trim()
    ) {
      setError("Please complete the required job posting fields.");
      return;
    }
    if (!canManage) {
      setError(
        "Only Admin, HR, and Team Leads can create or edit job postings.",
      );
      return;
    }
    setSaving(true);
    setError("");
    try {
      const payload: JobPostingInput = {
        ...form,
        job_title: form.job_title.trim(),
        job_description: form.job_description.trim(),
        required_skills: form.required_skills.trim(),
        required_experience: form.required_experience.trim(),
        hiring_request: form.hiring_request ?? null,
        closing_date: form.closing_date || null,
      };
      if (editingId) {
        const { data } = await recruitmentApi.updateJobPosting(
          editingId,
          payload,
        );
        setJobPostings((current) =>
          current.map((item) => (item.id === data.id ? data : item)),
        );
      } else {
        const { data } = await recruitmentApi.createJobPosting(payload);
        setJobPostings((current) => [data, ...current]);
      }
      resetForm();
    } catch {
      setError("We could not save this job posting.");
    } finally {
      setSaving(false);
    }
  }

  async function removePosting(id: number) {
    if (!canManage) return;
    try {
      await recruitmentApi.deleteJobPosting(id);
      setJobPostings((current) => current.filter((item) => item.id !== id));
      if (editingId === id) resetForm();
    } catch {
      setError("Only draft job postings can be deleted.");
    }
  }

  async function changeStatus(id: number, nextStatus: JobStatus) {
    if (!canManage) return;
    try {
      const { data } = await recruitmentApi.changeJobPostingStatus(
        id,
        nextStatus,
      );
      setJobPostings((current) =>
        current.map((item) => (item.id === data.id ? data : item)),
      );
    } catch {
      setError("We could not update this job posting status.");
    }
  }

  function canEditPosting(posting: JobPosting) {
    if (user?.role === "ADMIN" || user?.role === "HR") return true;
    if (user?.role === "TEAM_LEAD") {
      return (
        user.department === posting.department && posting.status === "DRAFT"
      );
    }
    return false;
  }

  function editPosting(posting: JobPosting) {
    if (!canEditPosting(posting)) return;
    setEditingId(posting.id);
    setForm({
      job_title: posting.job_title,
      job_description: posting.job_description,
      department: posting.department,
      hiring_request: posting.hiring_request,
      required_skills: posting.required_skills,
      required_experience: posting.required_experience,
      closing_date: posting.closing_date ?? "",
      cv_score_threshold: posting.cv_score_threshold,
      status: posting.status,
    });
  }

  if (loading)
    return <p className="py-8 text-sm text-ink/55">Loading job postings...</p>;

  return (
    <div className="min-w-0">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
          Talent pipeline
        </p>
        <h1 className="mt-2 font-display text-4xl font-bold tracking-tight sm:text-5xl">
          Job postings
        </h1>
        <p className="mt-3 max-w-2xl text-ink/55">
          Keep the active hiring pipeline aligned with approved departmental
          requests.
        </p>
      </div>
      {error && (
        <Alert className="mt-8" tone="error">
          {error}
        </Alert>
      )}

      {canManage && (
        <Card className="mt-10 border-0 bg-ink text-mist">
          <CardContent>
            <div className="flex items-start gap-3">
              <span className="grid h-10 w-10 place-items-center bg-coral text-ink">
                <Plus size={18} />
              </span>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
                  Manage
                </p>
                <h2 className="mt-1 font-display text-2xl font-bold">
                  {editingId ? "Edit posting" : "Create a posting"}
                </h2>
              </div>
            </div>
            <form onSubmit={submit} className="mt-8 space-y-5">
              <Field dark label="Job title" required>
                <Input
                  required
                  value={form.job_title}
                  onChange={(event) =>
                    setForm({ ...form, job_title: event.target.value })
                  }
                  placeholder="Senior product designer"
                  className="border-white/15 bg-white/10 text-mist placeholder:text-mist/40"
                />
              </Field>
              <div className="grid gap-5 sm:grid-cols-2">
                <Field dark label="Department" required>
                  <select
                    required
                    value={form.department || ""}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        department: Number(event.target.value),
                      })
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
                <Field dark label="Approved request">
                  <select
                    value={form.hiring_request ?? ""}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        hiring_request: event.target.value
                          ? Number(event.target.value)
                          : null,
                      })
                    }
                    className="mt-2 h-10 w-full rounded-lg border border-white/15 bg-white/10 px-3 text-sm text-mist"
                  >
                    <option value="" className="text-ink">
                      No linked request
                    </option>
                    {approvedHiringRequests.map((request) => (
                      <option
                        key={request.id}
                        value={request.id}
                        className="text-ink"
                      >
                        {request.request_title}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
              <Field dark label="Job description" required>
                <textarea
                  required
                  rows={4}
                  value={form.job_description}
                  onChange={(event) =>
                    setForm({ ...form, job_description: event.target.value })
                  }
                  className="mt-2 min-h-28 w-full resize-y rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-mist outline-none placeholder:text-mist/50 focus:border-coral"
                  placeholder="Describe the role, responsibilities, and impact."
                />
              </Field>
              <div className="grid gap-5 sm:grid-cols-2">
                <Field dark label="Required skills" required>
                  <textarea
                    required
                    rows={3}
                    value={form.required_skills}
                    onChange={(event) =>
                      setForm({ ...form, required_skills: event.target.value })
                    }
                    className="mt-2 min-h-24 w-full resize-y rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-mist outline-none placeholder:text-mist/50 focus:border-coral"
                    placeholder="Design systems, product strategy, stakeholder management"
                  />
                </Field>
                <Field dark label="Required experience" required>
                  <textarea
                    required
                    rows={3}
                    value={form.required_experience}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        required_experience: event.target.value,
                      })
                    }
                    className="mt-2 min-h-24 w-full resize-y rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-mist outline-none placeholder:text-mist/50 focus:border-coral"
                    placeholder="5+ years in SaaS, team leadership"
                  />
                </Field>
              </div>
              <div className="grid gap-5 sm:grid-cols-2">
                <Field dark label="Closing date">
                  <Input
                    type="date"
                    value={form.closing_date ?? ""}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        closing_date: event.target.value || "",
                      })
                    }
                    className="border-white/15 bg-white/10 text-mist"
                  />
                </Field>
                <Field dark label="ATS threshold">
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    value={form.cv_score_threshold}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        cv_score_threshold: Number(event.target.value) || 0,
                      })
                    }
                    className="border-white/15 bg-white/10 text-mist"
                  />
                </Field>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button
                  type="submit"
                  disabled={saving}
                  className="bg-coral text-ink hover:bg-coral/90"
                >
                  {saving
                    ? "Saving..."
                    : editingId
                      ? "Update posting"
                      : "Create posting"}
                </Button>
                {editingId && (
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Cancel
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <section className="mt-10 min-w-0">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
              Live list
            </p>
            <h2 className="mt-2 font-display text-2xl font-bold">
              Current postings
            </h2>
          </div>
          <span className="text-sm text-ink/45">
            {jobPostings.length} total
          </span>
        </div>
        <div className="mt-5 space-y-5">
          {jobPostings.length === 0 ? (
            <p className="border-y border-ink/10 py-10 text-sm text-ink/55">
              No job postings available.
            </p>
          ) : (
            jobPostings.map((posting) => (
              <Card key={posting.id} className="min-w-0 border-0 bg-white">
                <CardContent>
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-3">
                        <h3 className="break-words font-display text-2xl font-bold">
                          {posting.job_title}
                        </h3>
                        <Badge
                          className={
                            posting.status === "PUBLISHED"
                              ? "bg-mint text-ink"
                              : posting.status === "CLOSED"
                                ? "bg-coral text-ink"
                                : "bg-surface text-ink/60"
                          }
                        >
                          {posting.status}
                        </Badge>
                      </div>
                      <p className="mt-2 text-sm text-ink/55">
                        {posting.department_name} · {posting.applicant_count}{" "}
                        applicants
                      </p>
                      <p className="mt-3 max-w-3xl text-sm leading-6 text-ink/65">
                        {posting.job_description}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {posting.status === "PUBLISHED" && (
                        <Link to={`/recruitment/jobs/${posting.id}`}>
                          <Button type="button" variant="outline">
                            <Eye size={16} /> View details
                          </Button>
                        </Link>
                      )}
                      {canManage && (
                        <>
                          {posting.status !== "CLOSED" && (
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() =>
                                void changeStatus(
                                  posting.id,
                                  posting.status === "DRAFT"
                                    ? "PUBLISHED"
                                    : "CLOSED",
                                )
                              }
                            >
                              {posting.status === "DRAFT" ? "Publish" : "Close"}
                            </Button>
                          )}
                          {canEditPosting(posting) &&
                            posting.status === "DRAFT" && (
                              <Button
                                type="button"
                                variant="outline"
                                onClick={() => editPosting(posting)}
                              >
                                <PencilLine size={16} /> Edit
                              </Button>
                            )}
                          {posting.status === "DRAFT" && (
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => void removePosting(posting.id)}
                            >
                              <Trash2 size={16} /> Delete
                            </Button>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                  <dl className="mt-6 grid gap-4 border-t border-ink/10 pt-5 sm:grid-cols-3">
                    <Detail label="Skills" value={posting.required_skills} />
                    <Detail
                      label="Experience"
                      value={posting.required_experience}
                    />
                    <Detail
                      label="ATS threshold"
                      value={`${posting.cv_score_threshold}%`}
                    />
                  </dl>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </section>
    </div>
  );
}

function Field({
  label,
  required = false,
  dark = false,
  children,
}: {
  label: string;
  required?: boolean;
  dark?: boolean;
  children: ReactNode;
}) {
  return (
    <Label className={`block ${dark ? "text-mist/75" : "text-ink/70"}`}>
      {label}
      {required && <span className="ml-1 text-coral">*</span>}
      {children}
    </Label>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-bold uppercase tracking-[0.12em] text-ink/40">
        {label}
      </dt>
      <dd className="mt-1 text-sm text-ink/70">{value}</dd>
    </div>
  );
}
