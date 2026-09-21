import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { recruitmentApi } from "../api/recruitment";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import type { PublicJobPosting } from "../types";

export default function CareersPage() {
  const [jobs, setJobs] = useState<PublicJobPosting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadJobs() {
      try {
        const { data } = await recruitmentApi.listPublicJobs();
        setJobs(data);
      } catch {
        setError("We could not load the current openings right now.");
      } finally {
        setLoading(false);
      }
    }

    void loadJobs();
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-10">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-coral">
          Join our team
        </p>
        <h1 className="mt-3 font-display text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          Careers
        </h1>
        <p className="mt-3 max-w-2xl text-ink/60">
          Explore current openings and apply for roles that match your
          experience.
        </p>
      </div>

      {loading ? (
        <p className="text-ink/60">Loading roles...</p>
      ) : error ? (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">
          {error}
        </div>
      ) : jobs.length === 0 ? (
        <Card className="border-dashed border-ink/15 bg-white">
          <CardContent className="py-12 text-center text-ink/55">
            There are no published roles at the moment.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {jobs.map((job) => (
            <Card
              key={job.id}
              className="h-full border-ink/10 bg-white shadow-sm"
            >
              <CardContent className="flex h-full flex-col justify-between gap-5 p-6">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-coral">
                    {job.department_name}
                  </p>
                  <h2 className="mt-3 font-display text-2xl font-bold text-ink">
                    {job.job_title}
                  </h2>
                  <p className="mt-3 line-clamp-4 text-sm text-ink/60">
                    {job.job_description}
                  </p>
                </div>

                <div className="space-y-3 text-sm text-ink/60">
                  <div className="flex items-center justify-between gap-3">
                    <span>Experience</span>
                    <span className="font-medium text-ink">
                      {job.required_experience}
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span>Skills</span>
                    <span className="font-medium text-ink">
                      {job.required_skills}
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span>Closing date</span>
                    <span className="font-medium text-ink">
                      {job.closing_date
                        ? new Date(job.closing_date).toLocaleDateString()
                        : "Open"}
                    </span>
                  </div>
                </div>

                <Link to={`/careers/${job.id}`}>
                  <Button className="w-full">View role</Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
