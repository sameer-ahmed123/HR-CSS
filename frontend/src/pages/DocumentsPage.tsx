import { useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  Download,
  FileText,
  Loader2,
  Plus,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import client from "../api/client";
import {
  documentApi,
  type DocumentRequestItem,
  type DocumentTypeOption,
} from "../api/documents";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Card, CardContent } from "../components/ui/card";
import { Dialog, DialogContent, DialogTitle } from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { useAuth } from "../context/AuthContext";

const documentCodeOptions = ["SC", "APT_LET", "NOC", "EXP_LET", "ITC"];

function getStatusMeta(status: string) {
  const normalized = status?.toUpperCase();

  if (
    normalized === "READY" ||
    normalized === "DELIVERED" ||
    normalized === "APPROVED"
  ) {
    return {
      label: "Approved",
      badgeClass: "bg-emerald-100 text-emerald-700",
    };
  }

  if (normalized === "REJECTED") {
    return {
      label: "Rejected",
      badgeClass: "bg-red-100 text-red-700",
    };
  }

  return {
    label: "Pending",
    badgeClass: "bg-amber-100 text-amber-700",
  };
}

export default function DocumentsPage() {
  const { user } = useAuth();
  const [documentTypes, setDocumentTypes] = useState<DocumentTypeOption[]>([]);
  const [requests, setRequests] = useState<DocumentRequestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [rejectModal, setRejectModal] = useState({
    open: false,
    requestId: null as number | null,
    reason: "",
  });
  const [form, setForm] = useState({
    document_type: "",
    purpose: "",
    needed_by: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7)
      .toISOString()
      .slice(0, 10),
  });

  const roleIsHr = user ? ["ADMIN", "HR"].includes(user.role) : false;

  const pendingRequests = useMemo(
    () =>
      requests.filter((request) =>
        ["PENDING", "IN_PROGRESS"].includes(request.status.toUpperCase()),
      ),
    [requests],
  );

  const loadData = async () => {
    try {
      const [typesResponse, requestsResponse] = await Promise.all([
        documentApi.listDocumentTypes(),
        documentApi.listMyRequests(),
      ]);
      setDocumentTypes(typesResponse.data ?? []);
      setRequests(requestsResponse.data ?? []);
    } catch (error) {
      console.error("Unable to load documents data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  const handleCreateRequest = async () => {
    if (!form.document_type || !form.purpose.trim()) {
      return;
    }

    const selectedType = documentTypes.find(
      (type) => String(type.id) === form.document_type,
    );
    if (!selectedType) {
      return;
    }

    try {
      await documentApi.createRequest({
        document_type: selectedType.id,
        purpose: form.purpose,
        needed_by: form.needed_by,
      });
      setForm({
        document_type: "",
        purpose: "",
        needed_by: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7)
          .toISOString()
          .slice(0, 10),
      });
      setIsFormOpen(false);
      await loadData();
    } catch (error) {
      console.error("Unable to submit document request", error);
    }
  };

  const handleApprove = async (requestId: number) => {
    try {
      await documentApi.updateRequest(requestId, { status: "READY" });
      await loadData();
    } catch (error) {
      console.error("Unable to approve request", error);
    }
  };

  const handleReject = async () => {
    if (!rejectModal.requestId) {
      return;
    }

    const trimmedReason = rejectModal.reason.trim();
    if (!trimmedReason) {
      return;
    }

    try {
      await documentApi.updateRequest(rejectModal.requestId, {
        status: "REJECTED",
        rejection_reason: trimmedReason,
      });
      setRejectModal({ open: false, requestId: null, reason: "" });
      await loadData();
    } catch (error) {
      console.error("Unable to reject request", error);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-ink/60">
        <Loader2 className="mr-3 h-5 w-5 animate-spin" />
        Loading your requests...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-ink/45">
            Document center
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-ink">
            Document requests
          </h1>
        </div>
        <Button onClick={() => setIsFormOpen(true)} className="gap-2">
          <Plus size={16} />
          New request
        </Button>
      </div>

      <Card>
        <CardContent className="space-y-4 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-coral" />
              <h2 className="text-lg font-semibold text-ink">My requests</h2>
            </div>
            <Badge className="bg-surface px-2 py-1 text-ink/70">
              {requests.length} total
            </Badge>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm text-ink">
              <thead className="border-b border-ink/10 text-ink/60">
                <tr>
                  <th className="px-3 py-3 font-medium">Document type</th>
                  <th className="px-3 py-3 font-medium">Purpose</th>
                  <th className="px-3 py-3 font-medium">Status</th>
                  <th className="px-3 py-3 font-medium">Submitted</th>
                  <th className="px-3 py-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {requests.length === 0 ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-3 py-8 text-center text-ink/50"
                    >
                      No document requests yet.
                    </td>
                  </tr>
                ) : (
                  requests.map((request) => {
                    const statusMeta = getStatusMeta(request.status);
                    return (
                      <tr
                        key={request.id}
                        className="border-b border-ink/5 last:border-0"
                      >
                        <td className="px-3 py-3 font-medium">
                          {request.document_type_name}
                        </td>
                        <td className="px-3 py-3 max-w-xs truncate">
                          {request.purpose}
                        </td>
                        <td className="px-3 py-3">
                          <Badge
                            className={`${statusMeta.badgeClass} rounded-full px-2.5 py-1`}
                          >
                            {statusMeta.label}
                          </Badge>
                        </td>
                        <td className="px-3 py-3 text-ink/60">
                          {new Date(request.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-3 py-3">
                          {request.status?.toUpperCase() === "READY" ||
                          request.status?.toUpperCase() === "DELIVERED" ? (
                            request.generated_file ? (
                              <a
                                href={request.generated_file}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-2 rounded-lg bg-surface px-3 py-2 text-sm font-medium text-ink hover:bg-surface/80"
                              >
                                <Download size={15} />
                                Download PDF
                              </a>
                            ) : (
                              <span className="text-ink/45">Not available</span>
                            )
                          ) : (
                            <span className="text-ink/45">—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {roleIsHr && (
        <Card>
          <CardContent className="space-y-4 p-6">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-coral" />
              <h2 className="text-lg font-semibold text-ink">HR approvals</h2>
            </div>

            {pendingRequests.length === 0 ? (
              <p className="text-sm text-ink/60">
                No pending requests currently waiting for review.
              </p>
            ) : (
              <div className="space-y-3">
                {pendingRequests.map((request) => (
                  <div
                    key={request.id}
                    className="flex flex-col gap-3 rounded-2xl border border-ink/10 p-4 md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <p className="font-semibold text-ink">
                        {request.document_type_name}
                      </p>
                      <p className="text-sm text-ink/60">{request.purpose}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        className="gap-2"
                        onClick={() =>
                          setRejectModal({
                            open: true,
                            requestId: request.id,
                            reason: "",
                          })
                        }
                      >
                        <XCircle size={15} />
                        Reject
                      </Button>
                      <Button
                        className="gap-2"
                        onClick={() => handleApprove(request.id)}
                      >
                        <CheckCircle2 size={15} />
                        Approve
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Dialog
        open={rejectModal.open}
        onOpenChange={(open) =>
          setRejectModal((current) => ({ ...current, open }))
        }
      >
        <DialogContent>
          <DialogTitle className="text-xl font-semibold text-ink">
            Reject document request
          </DialogTitle>
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">
                Rejection reason
              </label>
              <textarea
                value={rejectModal.reason}
                onChange={(event) =>
                  setRejectModal((current) => ({
                    ...current,
                    reason: event.target.value,
                  }))
                }
                rows={4}
                className="w-full rounded-xl border border-ink/10 bg-white p-3 text-sm text-ink outline-none focus:ring-2 focus:ring-coral"
                placeholder="Explain why this document request is being rejected"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="outline"
                onClick={() =>
                  setRejectModal({ open: false, requestId: null, reason: "" })
                }
              >
                Cancel
              </Button>
              <Button
                onClick={handleReject}
                disabled={!rejectModal.reason.trim()}
                className="disabled:cursor-not-allowed disabled:opacity-50"
              >
                Confirm rejection
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
        <DialogContent>
          <DialogTitle className="text-xl font-semibold text-ink">
            Request a document
          </DialogTitle>
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">
                Document type
              </label>
              <select
                value={form.document_type}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    document_type: event.target.value,
                  }))
                }
                className="h-10 w-full rounded-lg border border-ink/10 bg-white px-3 text-sm text-ink outline-none focus:ring-2 focus:ring-coral"
              >
                <option value="">Select a document</option>
                {documentTypes.length > 0
                  ? documentTypes.map((type) => (
                      <option key={type.id} value={String(type.id)}>
                        {type.code} — {type.name}
                      </option>
                    ))
                  : documentCodeOptions.map((code) => (
                      <option key={code} value={code}>
                        {code}
                      </option>
                    ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">
                Required by
              </label>
              <Input
                type="date"
                value={form.needed_by}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    needed_by: event.target.value,
                  }))
                }
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">Purpose</label>
              <textarea
                value={form.purpose}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    purpose: event.target.value,
                  }))
                }
                rows={4}
                className="w-full rounded-xl border border-ink/10 bg-white p-3 text-sm text-ink outline-none focus:ring-2 focus:ring-coral"
                placeholder="Explain why you need this document"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setIsFormOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateRequest}>Submit request</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
