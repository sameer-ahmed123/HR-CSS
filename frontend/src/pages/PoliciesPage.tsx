import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCheck,
  CheckCircle2,
  FileText,
  Loader2,
  Plus,
  Send,
  ShieldCheck,
  Tag,
} from "lucide-react";
import {
  policyApi,
  type PolicyCategoryItem,
  type PolicyDetail,
  type PolicyItem,
} from "../api/policies";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Card, CardContent } from "../components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { useAuth } from "../context/AuthContext";

const defaultForm = {
  title: "",
  category: "",
  content: "",
  version: "1.0",
  is_mandatory: false,
  status: "DRAFT",
};

export default function PoliciesPage() {
  const { user } = useAuth();
  const [categories, setCategories] = useState<PolicyCategoryItem[]>([]);
  const [policies, setPolicies] = useState<PolicyItem[]>([]);
  const [selectedPolicy, setSelectedPolicy] = useState<PolicyDetail | null>(
    null,
  );
  const [pendingMandatory, setPendingMandatory] = useState<PolicyItem[]>([]);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [mandatoryOnly, setMandatoryOnly] = useState(false);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isComplianceOpen, setIsComplianceOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [policyForm, setPolicyForm] = useState(defaultForm);
  const [report, setReport] = useState<{
    acknowledged_users: any[];
    pending_users: any[];
  } | null>(null);

  const isHrOrAdmin = user ? ["ADMIN", "HR"].includes(user.role) : false;

  const visiblePolicies = useMemo(() => {
    return policies.filter((policy) => {
      const matchesSearch =
        !search || policy.title.toLowerCase().includes(search.toLowerCase());
      const matchesCategory =
        selectedCategory === "all" ||
        String(policy.category) === selectedCategory;
      const matchesMandatory = !mandatoryOnly || policy.is_mandatory;
      return matchesSearch && matchesCategory && matchesMandatory;
    });
  }, [policies, search, selectedCategory, mandatoryOnly]);

  const loadData = async () => {
    try {
      const filters: Record<string, string | number | boolean | undefined> = {};

      if (search.trim()) {
        filters.search = search.trim();
      }

      if (selectedCategory !== "all") {
        filters.category = selectedCategory;
      }

      if (mandatoryOnly) {
        filters.mandatory = true;
      }

      const [categoriesResponse, policiesResponse, pendingResponse] =
        await Promise.all([
          policyApi.listCategories(),
          policyApi.listPolicies(filters),
          policyApi.pendingAcknowledgements(),
        ]);

      setCategories(categoriesResponse.data ?? []);
      setPolicies(policiesResponse.data ?? []);
      setPendingMandatory(pendingResponse.data ?? []);
    } catch (error) {
      console.error("Failed to load policies", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, [search, selectedCategory, mandatoryOnly]);

  const openPolicyDetail = async (policy: PolicyItem) => {
    const detail = await policyApi.getPolicy(policy.id);
    setSelectedPolicy(detail.data);
    setIsDetailOpen(true);
  };

  const loadCompliance = async (policyId: number) => {
    try {
      const response = await policyApi.complianceReport(policyId);
      setReport(response.data);
      setIsComplianceOpen(true);
    } catch (error) {
      console.error("Failed to load compliance report", error);
    }
  };

  const handleCreatePolicy = async () => {
    try {
      await policyApi.createPolicy({
        title: policyForm.title,
        category: Number(policyForm.category),
        content: policyForm.content,
        version: policyForm.version,
        is_mandatory: policyForm.is_mandatory,
        status: policyForm.status,
        is_active: true,
      });
      setPolicyForm(defaultForm);
      setIsCreateOpen(false);
      await loadData();
    } catch (error) {
      console.error("Unable to create policy", error);
    }
  };

  const handleAcknowledge = async (policyId: number) => {
    try {
      await policyApi.acknowledgePolicy(policyId);
      setIsDetailOpen(false);
      await loadData();
    } catch (error) {
      console.error("Unable to acknowledge policy", error);
    }
  };

  const handleCreateVersion = async (policyId: number) => {
    const nextVersion = window.prompt(
      "Enter the next version string (e.g. 2.0)",
      "2.0",
    );
    const note = window.prompt("Add a change note", "Updated policy content");
    const content = window.prompt(
      "Paste the new policy content",
      selectedPolicy?.content ?? "",
    );

    if (!nextVersion || !content) {
      return;
    }

    try {
      await policyApi.createVersion(policyId, {
        new_version: nextVersion,
        content,
        change_note: note ?? "Updated policy content",
        effective_date: new Date().toISOString().slice(0, 10),
      });
      setIsDetailOpen(false);
      await loadData();
    } catch (error) {
      console.error("Unable to create new policy version", error);
    }
  };

  const handleSendReminder = async (policyId: number) => {
    try {
      const result = await policyApi.sendReminder(policyId);
      alert(`${result.data.count} reminder(s) sent.`);
    } catch (error) {
      console.error("Unable to send reminder", error);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-ink/60">
        <Loader2 className="mr-3 h-5 w-5 animate-spin" />
        Loading HR policy portal...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {pendingMandatory.length > 0 && (
        <div className="rounded-2xl border border-amber-300 bg-amber-50 p-4 text-amber-900">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5" />
            <div>
              <p className="font-semibold">
                You have pending mandatory policy acknowledgements
              </p>
              <p className="text-sm">
                Please review and acknowledge the latest required policies.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-ink/45">
            Employee portal
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-ink">Policies</h1>
        </div>
        {isHrOrAdmin && (
          <Button onClick={() => setIsCreateOpen(true)} className="gap-2">
            <Plus size={16} />
            Create policy
          </Button>
        )}
      </div>

      <div className="grid gap-6 xl:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="space-y-4 rounded-2xl border border-ink/10 bg-white p-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-ink">Search</label>
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search policy names..."
            />
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium text-ink">Categories</p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory("all")}
                className={`rounded-full px-3 py-1.5 text-xs font-semibold ${selectedCategory === "all" ? "bg-coral text-ink" : "bg-surface text-ink/70"}`}
              >
                All
              </button>
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(String(category.id))}
                  className={`rounded-full px-3 py-1.5 text-xs font-semibold ${selectedCategory === String(category.id) ? "bg-coral text-ink" : "bg-surface text-ink/70"}`}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm text-ink/70">
            <input
              type="checkbox"
              checked={mandatoryOnly}
              onChange={(e) => setMandatoryOnly(e.target.checked)}
            />
            Mandatory only
          </label>
        </aside>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {visiblePolicies.map((policy) => (
            <Card
              key={policy.id}
              className="cursor-pointer overflow-hidden transition hover:shadow-md"
              onClick={() => void openPolicyDetail(policy)}
            >
              <CardContent className="space-y-4 p-5">
                <div className="flex items-center justify-between gap-2">
                  <span className="inline-flex items-center rounded-full bg-surface px-2.5 py-1 text-[11px] font-medium text-ink/70">
                    <Tag size={12} className="mr-1" />
                    {categories.find(
                      (category) => category.id === policy.category,
                    )?.name ?? "General"}
                  </span>
                  {policy.is_acknowledged ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-1 text-[11px] font-semibold text-emerald-700">
                      <CheckCircle2 size={12} /> Acknowledged
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-1 text-[11px] font-semibold text-amber-700">
                      Pending
                    </span>
                  )}
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-ink">
                    {policy.title}
                  </h3>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Badge className="rounded-full bg-mint/70 px-2.5 py-1 text-[11px] font-semibold text-ink">
                    v{policy.version}
                  </Badge>
                  {policy.is_mandatory && (
                    <Badge className="rounded-full bg-red-100 px-2.5 py-1 text-[11px] font-semibold text-red-700">
                      Mandatory
                    </Badge>
                  )}
                </div>

                <p className="text-sm text-ink/60">
                  {policy.effective_date
                    ? `Effective: ${new Date(policy.effective_date).toLocaleDateString()}`
                    : "No effective date"}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogTitle className="text-xl font-semibold text-ink">
            Create policy
          </DialogTitle>
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">Title</label>
              <Input
                value={policyForm.title}
                onChange={(e) =>
                  setPolicyForm({ ...policyForm, title: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">Category</label>
              <select
                value={policyForm.category}
                onChange={(e) =>
                  setPolicyForm({ ...policyForm, category: e.target.value })
                }
                className="h-10 w-full rounded-lg border border-ink/10 bg-white px-3 text-sm text-ink outline-none focus:ring-2 focus:ring-coral"
              >
                <option value="">Select a category</option>
                {categories.map((category) => (
                  <option key={category.id} value={String(category.id)}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">Version</label>
              <Input
                value={policyForm.version}
                onChange={(e) =>
                  setPolicyForm({ ...policyForm, version: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">Content</label>
              <textarea
                value={policyForm.content}
                onChange={(e) =>
                  setPolicyForm({ ...policyForm, content: e.target.value })
                }
                rows={5}
                className="w-full rounded-xl border border-ink/10 bg-white p-3 text-sm text-ink outline-none focus:ring-2 focus:ring-coral"
              />
            </div>
            <label className="flex items-center gap-2 text-sm text-ink/70">
              <input
                type="checkbox"
                checked={policyForm.is_mandatory}
                onChange={(e) =>
                  setPolicyForm({
                    ...policyForm,
                    is_mandatory: e.target.checked,
                  })
                }
              />
              Mandatory policy
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreatePolicy}>Save policy</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="max-w-3xl">
          <DialogTitle className="text-xl font-semibold text-ink">
            {selectedPolicy?.title}
          </DialogTitle>
          <DialogDescription className="text-sm text-ink/60">
            Version {selectedPolicy?.version} ·{" "}
            {selectedPolicy?.is_mandatory ? "Mandatory" : "Optional"}
          </DialogDescription>

          {selectedPolicy && (
            <div className="mt-4 space-y-5">
              <div className="whitespace-pre-wrap rounded-2xl bg-surface p-4 text-sm leading-7 text-ink/80">
                {selectedPolicy.content}
              </div>

              <div className="space-y-3">
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-ink/45">
                  Version history
                </p>
                {selectedPolicy.version_history?.length ? (
                  selectedPolicy.version_history.map((entry) => (
                    <div
                      key={entry.id}
                      className="rounded-xl border border-ink/10 p-3"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-semibold text-ink">
                          v{entry.version}
                        </span>
                        <span className="text-xs text-ink/50">
                          {new Date(entry.effective_date).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-ink/70">
                        {entry.change_note || "No change note provided."}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-ink/60">
                    No version history available.
                  </p>
                )}
              </div>

              <div className="flex flex-wrap gap-2">
                {!selectedPolicy.is_acknowledged && (
                  <Button
                    className="gap-2"
                    onClick={() => void handleAcknowledge(selectedPolicy.id)}
                  >
                    <CheckCheck size={16} />I Acknowledge and Agree
                  </Button>
                )}

                {isHrOrAdmin && (
                  <>
                    <Button
                      variant="outline"
                      className="gap-2"
                      onClick={() =>
                        void handleCreateVersion(selectedPolicy.id)
                      }
                    >
                      <FileText size={16} />
                      New version
                    </Button>
                    <Button
                      variant="outline"
                      className="gap-2"
                      onClick={() => void loadCompliance(selectedPolicy.id)}
                    >
                      <ShieldCheck size={16} />
                      Compliance report
                    </Button>
                    <Button
                      variant="outline"
                      className="gap-2"
                      onClick={() => void handleSendReminder(selectedPolicy.id)}
                    >
                      <Send size={16} />
                      Send reminder
                    </Button>
                  </>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={isComplianceOpen} onOpenChange={setIsComplianceOpen}>
        <DialogContent className="max-w-3xl">
          <DialogTitle className="text-xl font-semibold text-ink">
            Compliance report
          </DialogTitle>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-ink/45">
                Acknowledged
              </p>
              {report?.acknowledged_users.length ? (
                report.acknowledged_users.map((user) => (
                  <div
                    key={user.id}
                    className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800"
                  >
                    <div className="font-semibold">{user.full_name}</div>
                    <div>{user.email}</div>
                    {user.department && <div>{user.department}</div>}
                  </div>
                ))
              ) : (
                <p className="text-sm text-ink/60">No acknowledgements yet.</p>
              )}
            </div>
            <div className="space-y-2">
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-ink/45">
                Pending
              </p>
              {report?.pending_users.length ? (
                report.pending_users.map((user) => (
                  <div
                    key={user.id}
                    className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800"
                  >
                    <div className="font-semibold">{user.full_name}</div>
                    <div>{user.email}</div>
                    {user.department && <div>{user.department}</div>}
                  </div>
                ))
              ) : (
                <p className="text-sm text-ink/60">
                  Everyone has acknowledged this policy.
                </p>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
