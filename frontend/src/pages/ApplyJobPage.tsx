import { Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { recruitmentApi } from "../api/recruitment";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import type { PublicJobPosting } from "../types";

type LinkItem = {
  id: number;
  label: string;
  url: string;
};

export default function ApplyJobPage() {
  const { jobId } = useParams();
  const [job, setJob] = useState<PublicJobPosting | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    address: "",
    cover_letter: "",
  });
  const [links, setLinks] = useState<LinkItem[]>([
    { id: 1, label: "", url: "" },
  ]);
  const [cvFile, setCvFile] = useState<File | null>(null);

  useEffect(() => {
    async function loadJob() {
      if (!jobId) {
        setError("This role is missing.");
        setLoading(false);
        return;
      }

      try {
        const { data } = await recruitmentApi.getPublicJob(Number(jobId));
        setJob(data);
      } catch {
        setError("This role is not available to apply for.");
      } finally {
        setLoading(false);
      }
    }

    void loadJob();
  }, [jobId]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!jobId || !cvFile) {
      setError("Please upload your CV before submitting.");
      return;
    }

    setSubmitting(true);
    setError("");
    setMessage("");

    const validLinks = links
      .filter((item) => item.url.trim())
      .map((item) => ({
        label: item.label.trim() || "Link",
        url: item.url.trim(),
      }));

    const payload = new FormData();
    payload.append("full_name", form.full_name);
    payload.append("email", form.email);
    payload.append("phone", form.phone);
    payload.append("address", form.address);
    payload.append("cover_letter", form.cover_letter);
    payload.append("links", JSON.stringify(validLinks));
    payload.append("cv", cvFile);

    try {
      await recruitmentApi.submitPublicApplication(Number(jobId), payload);
      setMessage("Your application has been submitted successfully.");
      setForm({
        full_name: "",
        email: "",
        phone: "",
        address: "",
        cover_letter: "",
      });
      setLinks([{ id: 1, label: "", url: "" }]);
      setCvFile(null);
    } catch (err) {
      const responseError = err as {
        response?: {
          data?: { error?: string; cv?: string[]; non_field_errors?: string[] };
        };
      };
      const serverMessage =
        responseError.response?.data?.error ??
        responseError.response?.data?.cv?.[0] ??
        responseError.response?.data?.non_field_errors?.[0] ??
        "We could not submit your application. Please try again.";
      setError(serverMessage);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading)
    return <p className="p-8 text-ink/60">Preparing application form...</p>;

  if (error && !job) {
    return (
      <div className="mx-auto max-w-xl p-8">
        <Card className="border-ink/10 bg-white">
          <CardContent className="p-8 text-center">
            <h1 className="font-display text-3xl font-bold text-ink">
              Application unavailable
            </h1>
            <p className="mt-3 text-ink/60">{error}</p>
            <Link to="/careers" className="mt-6 inline-block">
              <Button>View open roles</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-6">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-coral">
          {job?.department_name}
        </p>
        <h1 className="mt-2 font-display text-4xl font-bold tracking-tight text-ink">
          Apply for {job?.job_title}
        </h1>
      </div>

      <Card className="border-ink/10 bg-white shadow-sm">
        <CardContent className="p-6 sm:p-8">
          {message ? (
            <div className="mb-6 rounded-2xl border border-green-200 bg-green-50 px-4 py-3 text-green-700">
              {message}
            </div>
          ) : null}

          {error ? (
            <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">
              {error}
            </div>
          ) : null}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="mb-2 block text-sm font-medium text-ink">
                Full name
              </label>
              <Input
                value={form.full_name}
                onChange={(event) =>
                  setForm({ ...form, full_name: event.target.value })
                }
                placeholder="Your full name"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-ink">
                Email address
              </label>
              <Input
                type="email"
                value={form.email}
                onChange={(event) =>
                  setForm({ ...form, email: event.target.value })
                }
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-ink">
                Phone number
              </label>
              <Input
                value={form.phone}
                onChange={(event) =>
                  setForm({ ...form, phone: event.target.value })
                }
                placeholder="Optional"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-ink">
                Address
              </label>
              <Input
                value={form.address}
                onChange={(event) =>
                  setForm({ ...form, address: event.target.value })
                }
                placeholder="Your current address"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-ink">
                Cover letter
              </label>
              <textarea
                value={form.cover_letter}
                onChange={(event) =>
                  setForm({ ...form, cover_letter: event.target.value })
                }
                placeholder="Tell us why you are a fit for this role"
                className="min-h-32 w-full rounded-lg border border-ink/15 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-ink/35 focus-visible:ring-2 focus-visible:ring-coral"
              />
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between gap-3">
                <label className="block text-sm font-medium text-ink">
                  Links
                </label>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() =>
                    setLinks((current) => [
                      ...current,
                      { id: Date.now() + Math.random(), label: "", url: "" },
                    ])
                  }
                >
                  <Plus size={16} />
                </Button>
              </div>

              <div className="space-y-3">
                {links.map((item, index) => (
                  <div
                    key={item.id}
                    className="grid gap-2 sm:grid-cols-[180px_1fr_auto]"
                  >
                    <Input
                      value={item.label}
                      onChange={(event) => {
                        const nextLinks = [...links];
                        nextLinks[index] = {
                          ...nextLinks[index],
                          label: event.target.value,
                        };
                        setLinks(nextLinks);
                      }}
                      placeholder="GitHub"
                    />
                    <Input
                      value={item.url}
                      onChange={(event) => {
                        const nextLinks = [...links];
                        nextLinks[index] = {
                          ...nextLinks[index],
                          url: event.target.value,
                        };
                        setLinks(nextLinks);
                      }}
                      placeholder="https://github.com/yourname"
                    />
                    {links.length > 1 ? (
                      <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={() =>
                          setLinks((current) =>
                            current.filter((link) => link.id !== item.id),
                          )
                        }
                        aria-label="Remove link"
                      >
                        <Trash2 size={16} />
                      </Button>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-ink">
                Upload CV
              </label>
              <Input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(event) => setCvFile(event.target.files?.[0] ?? null)}
                required
              />
            </div>

            <div className="flex flex-col gap-3 pt-2 sm:flex-row">
              <Link to={`/careers/${job?.id ?? ""}`} className="sm:order-2">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full sm:w-auto"
                >
                  Cancel
                </Button>
              </Link>
              <Button
                type="submit"
                disabled={submitting}
                className="w-full sm:w-auto"
              >
                {submitting ? "Submitting..." : "Submit application"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
