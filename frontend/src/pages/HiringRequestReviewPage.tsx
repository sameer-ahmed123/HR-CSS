import { Check, CircleHelp, X } from "lucide-react";
import { useEffect, useState } from "react";
import { recruitmentApi } from "../api/recruitment";
import { Alert } from "../components/ui/alert";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "../components/ui/dialog";
import type { HiringRequest } from "../types";

export default function HiringRequestReviewPage() {
  const [requests, setRequests] = useState<HiringRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [workingId, setWorkingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [rejectionReasons, setRejectionReasons] = useState<
    Record<number, string>
  >({});
  const [approvalPrompt, setApprovalPrompt] = useState<number | null>(null);

  useEffect(() => {
    async function loadRequests() {
      try {
        const { data } = await recruitmentApi.listHiringRequests();
        setRequests(data);
      } catch {
        setError("We could not load the hiring request queue.");
      } finally {
        setLoading(false);
      }
    }
    void loadRequests();
  }, []);

  async function updateStatus(
    id: number,
    status: "APPROVED" | "REJECTED" | "MORE_INFO",
    createJobPosting = false,
  ) {
    const rejectionReason = rejectionReasons[id]?.trim();
    if (status === "REJECTED" && !rejectionReason) {
      setError("A rejection reason is required before rejecting a request.");
      return;
    }

    setWorkingId(id);
    setError("");
    try {
      const { data } = await recruitmentApi.updateHiringRequestStatus(
        id,
        status,
        rejectionReason,
        createJobPosting,
      );
      setRequests((current) =>
        current.map((request) => (request.id === id ? data : request)),
      );
    } catch {
      setError("We could not update this request. Please try again.");
    } finally {
      setWorkingId(null);
    }
  }

  const pendingRequests = requests.filter(
    (request) => request.status === "PENDING",
  );

  return (
    <div className="min-w-0">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
          Approval queue
        </p>
        <h1 className="mt-2 font-display text-4xl font-bold tracking-tight sm:text-5xl">
          Review hiring requests
        </h1>
        <p className="mt-3 max-w-2xl text-ink/55">
          Approve workforce requests, ask for more information, or record a
          clear rejection reason.
        </p>
      </div>
      {error && (
        <Alert className="mt-8" tone="error">
          {error}
        </Alert>
      )}
      {loading ? (
        <p className="py-10 text-sm text-ink/55">Loading approval queue...</p>
      ) : (
        <section className="mt-10">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
                Pending review
              </p>
              <h2 className="mt-2 font-display text-2xl font-bold">
                Requests awaiting a decision
              </h2>
            </div>
            <span className="text-sm text-ink/45">
              {pendingRequests.length} pending
            </span>
          </div>
          <div className="mt-5 min-w-0 space-y-5">
            {pendingRequests.length === 0 ? (
              <p className="border-y border-ink/10 py-10 text-sm text-ink/55">
                The approval queue is clear.
              </p>
            ) : (
              pendingRequests.map((request) => (
                <RequestCard
                  key={request.id}
                  request={request}
                  rejectionReason={rejectionReasons[request.id] ?? ""}
                  working={workingId === request.id}
                  onRejectionReasonChange={(value) =>
                    setRejectionReasons((current) => ({
                      ...current,
                      [request.id]: value,
                    }))
                  }
                  onApprove={() => setApprovalPrompt(request.id)}
                  onStatusChange={(status) =>
                    void updateStatus(request.id, status)
                  }
                />
              ))
            )}
          </div>
        </section>
      )}

      <Dialog
        open={approvalPrompt !== null}
        onOpenChange={(open) => {
          if (!open) setApprovalPrompt(null);
        }}
      >
        <DialogContent className="max-w-md">
          <DialogTitle className="font-display text-2xl font-bold">
            Create a job posting?
          </DialogTitle>
          <DialogDescription className="mt-3 text-sm leading-6 text-ink/60">
            This approved request will be turned into a draft job posting and
            added to the job postings list for HR to publish later.
          </DialogDescription>
          <div className="mt-6 flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => setApprovalPrompt(null)}
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={() => {
                if (approvalPrompt !== null) {
                  void updateStatus(approvalPrompt, "APPROVED", true);
                  setApprovalPrompt(null);
                }
              }}
            >
              Create posting
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function RequestCard({
  request,
  rejectionReason,
  working,
  onRejectionReasonChange,
  onApprove,
  onStatusChange,
}: {
  request: HiringRequest;
  rejectionReason: string;
  working: boolean;
  onRejectionReasonChange: (value: string) => void;
  onApprove: () => void;
  onStatusChange: (status: "APPROVED" | "REJECTED" | "MORE_INFO") => void;
}) {
  return (
    <Card className="min-w-0 border-0 bg-white">
      <CardContent>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h3 className="break-words font-display text-2xl font-bold">
                {request.request_title}
              </h3>
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
            <p className="mt-2 text-sm text-ink/55">
              {request.headcount} position{request.headcount === 1 ? "" : "s"} ·{" "}
              {request.seniority} · Requested{" "}
              {new Date(request.created_at).toLocaleDateString()}
            </p>
          </div>
          <Badge className="w-fit bg-mint text-ink">{request.status}</Badge>
        </div>
        <dl className="mt-6 grid gap-4 border-t border-ink/10 pt-5 sm:grid-cols-2">
          <Detail label="Reason" value={request.reason} />
          <Detail label="Experience" value={request.required_experience} />
          <Detail
            label="Qualifications"
            value={request.required_qualifications}
          />
          <Detail
            label="Budget"
            value={request.budget ? request.budget : "Not specified"}
          />
        </dl>
        <div className="mt-6 border-t border-ink/10 pt-5">
          <label
            className="block text-sm font-semibold"
            htmlFor={`rejection-${request.id}`}
          >
            Rejection reason
            <textarea
              id={`rejection-${request.id}`}
              value={rejectionReason}
              onChange={(event) => onRejectionReasonChange(event.target.value)}
              rows={2}
              placeholder="Required only when rejecting"
              className="mt-2 w-full rounded-lg border border-ink/15 bg-white px-3 py-2 text-sm outline-none focus:border-coral"
            />
          </label>
          <div className="mt-4 grid gap-3 sm:flex sm:flex-wrap">
            <Button type="button" disabled={working} onClick={onApprove}>
              <Check size={16} /> Approve
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={working}
              onClick={() => onStatusChange("MORE_INFO")}
            >
              <CircleHelp size={16} /> Request more info
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={working}
              onClick={() => onStatusChange("REJECTED")}
            >
              <X size={16} /> Reject
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
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
