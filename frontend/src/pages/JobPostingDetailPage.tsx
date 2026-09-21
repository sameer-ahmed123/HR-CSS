import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Download,
  Mail,
  MapPin,
  Phone,
  UserRound,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { recruitmentApi } from "../api/recruitment";
import { Alert } from "../components/ui/alert";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import type {
  JobPosting,
  JobPostingApplication,
  JobPostingApplicationDetail,
} from "../types";

export default function JobPostingDetailPage() {
  const { jobId, applicationId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState<JobPosting | null>(null);
  const [applications, setApplications] = useState<JobPostingApplication[]>([]);
  const [selectedApplication, setSelectedApplication] =
    useState<JobPostingApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingApplication, setLoadingApplication] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      if (!jobId) return;

      try {
        const { data: jobData } = await recruitmentApi.getJobPosting(
          Number(jobId),
        );
        const { data: listData } =
          await recruitmentApi.listJobPostingApplications(Number(jobId));

        setJob(jobData);
        setApplications(listData);

        if (applicationId) {
          const { data: appData } =
            await recruitmentApi.getJobPostingApplication(
              Number(jobId),
              Number(applicationId),
            );
          setSelectedApplication(appData);
        }
      } catch {
        setError("We could not load the job posting and applicant list.");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [jobId, applicationId]);

  const selectedCvUrl = useMemo(() => {
    if (!selectedApplication?.attached_cv) return null;
    const url = selectedApplication.attached_cv;
    if (!url) return null;
    if (/^https?:\/\//i.test(url)) return url;
    return url.startsWith("/") ? url : `/${url}`;
  }, [selectedApplication]);

  const isPdfCv = selectedCvUrl?.toLowerCase().endsWith(".pdf") ?? false;

  async function openApplication(applicationIdNumber: number) {
    if (!jobId) return;

    try {
      setLoadingApplication(true);
      const { data } = await recruitmentApi.getJobPostingApplication(
        Number(jobId),
        applicationIdNumber,
      );
      setSelectedApplication(data);
      navigate(
        `/recruitment/jobs/${jobId}/applications/${applicationIdNumber}`,
      );
    } catch {
      setError("We could not load this application.");
    } finally {
      setLoadingApplication(false);
    }
  }

  if (loading) {
    return <p className="py-8 text-sm text-ink/55">Loading job posting...</p>;
  }

  if (error || !job) {
    return (
      <div className="max-w-2xl">
        <Alert tone="error">
          {error || "This job posting could not be found."}
        </Alert>
        <Link to="/recruitment/jobs" className="mt-4 inline-block">
          <Button type="button" variant="outline">
            Back to job postings
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="min-w-0 space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Link
          to="/recruitment/jobs"
          className="inline-flex items-center gap-2 text-sm font-semibold text-ink/70 hover:text-ink"
        >
          <ArrowLeft size={16} /> Back to postings
        </Link>
        <Badge
          className={
            job.status === "PUBLISHED"
              ? "bg-mint text-ink"
              : "bg-surface text-ink/60"
          }
        >
          {job.status}
        </Badge>
      </div>

      <Card className="border-0 bg-white">
        <CardContent className="p-6 sm:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
                {job.department_name}
              </p>
              <h1 className="mt-2 font-display text-4xl font-bold tracking-tight">
                {job.job_title}
              </h1>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge className="bg-surface text-ink/65">
                ATS {job.cv_score_threshold}%
              </Badge>
              <Badge className="bg-coral/10 text-ink">
                {job.applicant_count} applicants
              </Badge>
            </div>
          </div>

          <div className="mt-8 grid gap-4 border-t border-ink/10 pt-6 sm:grid-cols-2 xl:grid-cols-4">
            <DetailTile label="Skills" value={job.required_skills} />
            <DetailTile label="Experience" value={job.required_experience} />
            <DetailTile
              label="Closing date"
              value={
                job.closing_date
                  ? new Date(job.closing_date).toLocaleDateString()
                  : "Open"
              }
            />
            <DetailTile
              label="Hiring request"
              value={
                job.hiring_request
                  ? `#${job.hiring_request}`
                  : "Independent posting"
              }
            />
          </div>

          <div className="mt-8">
            <h2 className="font-display text-2xl font-bold">
              Role description
            </h2>
            <p className="mt-3 whitespace-pre-line text-sm leading-7 text-ink/70">
              {job.job_description}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="border-0 bg-white">
        <CardContent className="p-4 sm:p-6">
          <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
                Candidate pipeline
              </p>
              <h2 className="mt-2 font-display text-3xl font-bold">
                Submitted applications
              </h2>
            </div>
            <span className="text-sm text-ink/50">
              {applications.length} total
            </span>
          </div>

          {applications.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-ink/15 py-10 text-center text-sm text-ink/55">
              No applications have been submitted for this role yet.
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-ink/10">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead>Candidate</TableHead>
                    <TableHead>Stage</TableHead>
                    <TableHead>ATS</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Applied</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {applications.map((application) => (
                    <TableRow
                      key={application.id}
                      className={
                        selectedApplication?.id === application.id
                          ? "bg-surface/80"
                          : "cursor-pointer"
                      }
                      onClick={() => void openApplication(application.id)}
                    >
                      <TableCell>
                        <div className="min-w-48">
                          <p className="font-semibold text-ink">
                            {application.candidate_name}
                          </p>
                          <p className="mt-1 text-sm text-ink/55">
                            {application.candidate_email}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className="bg-surface text-ink/70">
                          {application.stage_label}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-semibold text-coral">
                        {application.ats_score}
                      </TableCell>
                      <TableCell>
                        {application.is_priority ? (
                          <Badge className="bg-mint text-ink">Priority</Badge>
                        ) : (
                          <span className="text-sm text-ink/45">Normal</span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-ink/55">
                        {new Date(application.created_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {selectedApplication && (
        <Card className="border-0 bg-ink text-mist">
          <CardContent className="p-6 sm:p-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
                  Application detail
                </p>
                <h3 className="mt-2 font-display text-3xl font-bold">
                  {selectedApplication.candidate.candidate_name}
                </h3>
              </div>
              {loadingApplication ? (
                <span className="text-sm text-mist/60">Loading...</span>
              ) : (
                <Badge className="bg-surface text-ink/70">
                  {selectedApplication.stage_label}
                </Badge>
              )}
            </div>

            <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
              <InfoPill
                icon={Mail}
                label="Email"
                value={selectedApplication.candidate.email}
              />
              <InfoPill
                icon={Phone}
                label="Phone"
                value={
                  selectedApplication.candidate.phone_number || "Not provided"
                }
              />
              <InfoPill
                icon={MapPin}
                label="Location"
                value={selectedApplication.candidate.location || "Not provided"}
              />
              <InfoPill
                icon={CalendarDays}
                label="Applied"
                value={new Date(
                  selectedApplication.created_at,
                ).toLocaleDateString()}
              />
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-xl border border-white/10 bg-white/5 p-5">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.12em] text-coral">
                  <UserRound size={16} /> Candidate summary
                </div>
                <p className="text-sm leading-7 text-mist/75">
                  {selectedApplication.candidate.about ||
                    "No profile summary provided."}
                </p>
              </div>

              <div className="space-y-4 rounded-xl border border-white/10 bg-white/5 p-5">
                <div className="flex items-center justify-between text-sm text-mist/70">
                  <span>ATS score</span>
                  <span className="text-xl font-bold text-coral">
                    {selectedApplication.ats_score}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm text-mist/70">
                  <span>Priority</span>
                  <span>{selectedApplication.is_priority ? "Yes" : "No"}</span>
                </div>
                <div className="flex items-center justify-between text-sm text-mist/70">
                  <span>Stage</span>
                  <span>{selectedApplication.stage_label}</span>
                </div>
                {selectedCvUrl ? (
                  <div className="space-y-3">
                    {isPdfCv ? (
                      <div className="overflow-hidden rounded-xl border border-white/10 bg-white/5">
                        <iframe
                          title="Applicant CV preview"
                          src={selectedCvUrl}
                          className="h-[420px] w-full bg-white"
                        />
                      </div>
                    ) : null}
                    <a href={selectedCvUrl} target="_blank" rel="noreferrer">
                      <Button
                        type="button"
                        variant="outline"
                        className="w-full border-white/15 bg-white/5 text-mist hover:bg-white/10"
                      >
                        <Download size={16} /> Open / download CV
                      </Button>
                    </a>
                  </div>
                ) : (
                  <div className="rounded-lg border border-dashed border-white/15 px-3 py-2 text-sm text-mist/50">
                    No CV available
                  </div>
                )}
              </div>
            </div>

            {selectedApplication.score_reasons &&
              Object.keys(selectedApplication.score_reasons).length > 0 && (
                <div className="mt-8 rounded-xl border border-white/10 bg-white/5 p-5">
                  <div className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.12em] text-coral">
                    <CheckCircle2 size={16} /> ATS breakdown
                  </div>
                  <ul className="space-y-2 text-sm text-mist/70">
                    {Object.entries(selectedApplication.score_reasons).map(
                      ([key, value]) => (
                        <li
                          key={key}
                          className="flex items-center justify-between gap-4 border-b border-white/10 pb-2 last:border-0 last:pb-0"
                        >
                          <span>{key.replace(/_/g, " ")}</span>
                          <span>{String(value)}</span>
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function DetailTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-ink/10 bg-surface px-4 py-3">
      <p className="text-xs font-bold uppercase tracking-[0.12em] text-ink/45">
        {label}
      </p>
      <p className="mt-2 text-sm text-ink/70">{value}</p>
    </div>
  );
}

function InfoPill({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Mail;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-coral">
        <Icon size={14} />
        {label}
      </div>
      <p className="mt-2 break-all text-sm text-mist/80">{value}</p>
    </div>
  );
}
