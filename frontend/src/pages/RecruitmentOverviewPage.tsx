import { BriefcaseBusiness, Clock3, Mail, Star, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { recruitmentApi } from "../api/recruitment";
import { Alert } from "../components/ui/alert";
import { Badge } from "../components/ui/badge";
import { Card, CardContent } from "../components/ui/card";
import type { RecruitmentOverview } from "../types";

const funnelStages = [
  "NEW",
  "REVIEWED",
  "SHORTLISTED",
  "TEST_SENT",
  "INTERVIEW",
  "OFFER",
  "HIRED",
] as const;

export default function RecruitmentOverviewPage() {
  const [overview, setOverview] = useState<RecruitmentOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadOverview() {
      try {
        const { data } = await recruitmentApi.getOverview();
        setOverview(data);
      } catch {
        setError(
          "We could not load the recruitment overview. Please try again.",
        );
      } finally {
        setLoading(false);
      }
    }
    void loadOverview();
  }, []);

  if (loading)
    return <p className="py-8 text-sm text-ink/55">Loading recruitment...</p>;
  if (error) return <Alert tone="error">{error}</Alert>;
  if (!overview) return null;

  return (
    <div className="min-w-0">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
          Talent operations
        </p>
        <h1 className="mt-2 font-display text-4xl font-bold tracking-tight sm:text-5xl">
          Recruitment
        </h1>
        <p className="mt-3 max-w-2xl text-ink/55">
          Keep hiring momentum visible from workforce request to candidate
          pipeline.
        </p>
      </div>

      <div className="mt-10 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric
          icon={BriefcaseBusiness}
          label="Open jobs"
          value={overview.total_open_jobs}
        />
        <Metric
          icon={Clock3}
          label="Pending requests"
          value={overview.pending_hiring_requests_count}
        />
        <Metric
          icon={Users}
          label="New applications"
          value={overview.new_applications_this_week}
        />
        <Metric
          icon={Mail}
          label="Emails this week"
          value={overview.emails_sent_this_week}
        />
      </div>

      <div className="mt-10 grid min-w-0 gap-8 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
        <section>
          <SectionHeading eyebrow="Live roles" title="Open jobs" />
          <div className="mt-5 divide-y divide-ink/10 border-y border-ink/10">
            {overview.open_jobs.length === 0 ? (
              <Empty text="No published jobs yet." />
            ) : (
              overview.open_jobs.map((job) => (
                <div
                  key={job.id}
                  className="flex flex-col gap-3 py-5 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <h2 className="font-display text-xl font-bold">
                      {job.job_title}
                    </h2>
                    <p className="mt-1 text-sm text-ink/55">
                      {job.department_name}
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-xs uppercase tracking-[0.12em] text-ink/45">
                    <span>{job.applicant_count} applicants</span>
                    <Badge className="bg-mint text-ink">{job.status}</Badge>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        <section>
          <SectionHeading eyebrow="Candidate flow" title="Pipeline" />
          <Card className="mt-5 border-0 bg-ink text-mist">
            <CardContent className="space-y-4">
              {funnelStages.map((stage) => {
                const count = overview.pipeline_funnel[stage] ?? 0;
                const max = Math.max(
                  ...funnelStages.map(
                    (item) => overview.pipeline_funnel[item] ?? 0,
                  ),
                  1,
                );
                return (
                  <div key={stage}>
                    <div className="flex justify-between text-xs uppercase tracking-[0.12em] text-mist/60">
                      <span>{stage.replace("_", " ")}</span>
                      <span>{count}</span>
                    </div>
                    <div className="mt-2 h-2 bg-white/10">
                      <div
                        className="h-full bg-coral"
                        style={{ width: `${(count / max) * 100}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </section>
      </div>

      <div className="mt-10 grid min-w-0 gap-8 xl:grid-cols-2">
        <section>
          <SectionHeading
            eyebrow="Needs review"
            title="Pending hiring requests"
          />
          <div className="mt-5 divide-y divide-ink/10 border-y border-ink/10">
            {overview.pending_hiring_requests.length === 0 ? (
              <Empty text="No pending requests." />
            ) : (
              overview.pending_hiring_requests.map((request) => (
                <div
                  key={request.id}
                  className="flex items-center justify-between gap-4 py-4"
                >
                  <div>
                    <h2 className="break-words font-semibold">
                      {request.request_title}
                    </h2>
                    <p className="mt-1 text-sm text-ink/55">
                      {request.department_name} · {request.requested_by_name}
                    </p>
                  </div>
                  <Badge
                    className={
                      request.urgency === "URGENT"
                        ? "bg-coral text-ink"
                        : "bg-surface text-ink/60"
                    }
                  >
                    {request.urgency}
                  </Badge>
                </div>
              ))
            )}
          </div>
        </section>

        <section>
          <SectionHeading
            eyebrow="Priority talent"
            title="Priority candidates"
          />
          <div className="mt-5 divide-y divide-ink/10 border-y border-ink/10">
            {overview.priority_candidates.length === 0 ? (
              <Empty text="No priority candidates yet." />
            ) : (
              overview.priority_candidates.map((candidate) => (
                <div
                  key={candidate.id}
                  className="flex items-center justify-between gap-4 py-4"
                >
                  <div>
                    <h2 className="break-words font-semibold">
                      {candidate.candidate_name}
                    </h2>
                    <p className="mt-1 text-sm text-ink/55">
                      {candidate.job_title} ·{" "}
                      {candidate.stage.replace("_", " ")}
                    </p>
                  </div>
                  <span className="flex items-center gap-1 text-sm font-bold text-coral">
                    <Star size={15} /> {candidate.ats_score}
                  </span>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof BriefcaseBusiness;
  label: string;
  value: number;
}) {
  return (
    <Card className="border-0 bg-white">
      <CardContent>
        <Icon size={21} className="text-coral" />
        <p className="mt-8 text-sm text-ink/55">{label}</p>
        <p className="mt-1 font-display text-4xl font-bold">{value}</p>
      </CardContent>
    </Card>
  );
}

function SectionHeading({
  eyebrow,
  title,
}: {
  eyebrow: string;
  title: string;
}) {
  return (
    <div>
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
        {eyebrow}
      </p>
      <h2 className="mt-2 font-display text-2xl font-bold">{title}</h2>
    </div>
  );
}

function Empty({ text }: { text: string }) {
  return <p className="py-8 text-sm text-ink/55">{text}</p>;
}
