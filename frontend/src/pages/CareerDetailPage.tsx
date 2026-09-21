import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { recruitmentApi } from "../api/recruitment";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import type { PublicJobPosting } from "../types";

export default function CareerDetailPage() {
  const { jobId } = useParams();
  const [job, setJob] = useState<PublicJobPosting | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadJob() {
      if (!jobId) {
        setError("This role could not be found.");
        setLoading(false);
        return;
      }

      try {
        const { data } = await recruitmentApi.getPublicJob(Number(jobId));
        setJob(data);
      } catch {
        setError("This role is not available or has expired.");
      } finally {
        setLoading(false);
      }
    }

    void loadJob();
  }, [jobId]);

  if (loading)
    return <p className="p-8 text-ink/60">Loading role details...</p>;
  if (error) {
    return (
      <div className="mx-auto max-w-3xl p-8">
        <Card className="border-ink/10 bg-white">
          <CardContent className="p-8 text-center">
            <h1 className="font-display text-3xl font-bold text-ink">
              Role unavailable
            </h1>
            <p className="mt-3 text-ink/60">{error}</p>
            <Link to="/careers" className="mt-6 inline-block">
              <Button>Back to careers</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!job) return null;

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-coral">
            {job.department_name}
          </p>
          <h1 className="mt-2 font-display text-4xl font-bold tracking-tight text-ink">
            {job.job_title}
          </h1>
        </div>
        <Link to={`/careers/${job.id}/apply`}>
          <Button size="lg">Apply now</Button>
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(280px,0.6fr)]">
        <Card className="border-ink/10 bg-white">
          <CardContent className="space-y-6 p-6">
            <section>
              <h2 className="font-display text-2xl font-bold text-ink">
                Role description
              </h2>
              <p className="mt-3 whitespace-pre-line text-ink/70">
                {job.job_description}
              </p>
            </section>

            <section>
              <h2 className="font-display text-xl font-bold text-ink">
                Requirements
              </h2>
              <ul className="mt-3 list-disc space-y-2 pl-5 text-ink/70">
                <li>{job.required_experience}</li>
                <li>{job.required_skills}</li>
              </ul>
            </section>
          </CardContent>
        </Card>

        <Card className="border-ink/10 bg-white">
          <CardContent className="space-y-4 p-6">
            <div>
              <p className="text-xs uppercase tracking-[0.14em] text-ink/45">
                Application threshold
              </p>
              <p className="mt-2 text-2xl font-bold text-ink">
                {job.cv_score_threshold}%
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.14em] text-ink/45">
                Experience
              </p>
              <p className="mt-2 text-base font-semibold text-ink">
                {job.required_experience}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.14em] text-ink/45">
                Closing date
              </p>
              <p className="mt-2 text-base font-semibold text-ink">
                {job.closing_date
                  ? new Date(job.closing_date).toLocaleDateString()
                  : "Open until filled"}
              </p>
            </div>
            <Link to="/careers">
              <Button variant="outline" className="w-full">
                Browse other roles
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
