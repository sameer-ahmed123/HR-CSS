import client from "./client";

export interface PolicyCategoryItem {
  id: number;
  name: string;
  description?: string | null;
  is_active?: boolean;
  total_policies?: number;
}

export interface PolicyItem {
  id: number;
  title: string;
  version: string;
  status?: string;
  effective_date?: string | null;
  is_mandatory: boolean;
  is_active: boolean;
  is_acknowledged?: boolean;
  category?: number;
}

export interface PolicyVersionHistory {
  id: number;
  version: string;
  content: string;
  change_note: string;
  effective_date: string;
  created_at: string;
}

export interface PolicyDetail extends PolicyItem {
  category: number;
  content: string;
  document_file?: string | null;
  created_by?: number | null;
  version_history: PolicyVersionHistory[];
}

export interface ComplianceReportResponse {
  acknowledged_users: Array<{
    id: number;
    full_name: string;
    email: string;
    department: string | null;
    acknowledged: boolean;
    acknowledged_at: string | null;
  }>;
  pending_users: Array<{
    id: number;
    full_name: string;
    email: string;
    department: string | null;
    acknowledged: boolean;
    acknowledged_at: string | null;
  }>;
}

export const policyApi = {
  listCategories: () => client.get<PolicyCategoryItem[]>("/policies/categories/"),
  listPolicies: (params?: Record<string, string | boolean | number | undefined>) =>
    client.get<PolicyItem[]>("/policies/", { params }),
  getPolicy: (id: number) => client.get<PolicyDetail>(`/policies/${id}/`),
  createPolicy: (payload: Record<string, unknown>) => client.post<PolicyDetail>("/policies/", payload),
  acknowledgePolicy: (id: number) => client.post<{ detail: string; id?: number }>(`/policies/${id}/acknowledge/`, {}),
  createVersion: (id: number, payload: Record<string, unknown>) =>
    client.post<PolicyDetail>(`/policies/${id}/create-version/`, payload),
  archivePolicy: (id: number) => client.patch<PolicyDetail>(`/policies/${id}/archive/`, {}),
  complianceReport: (id: number) => client.get<ComplianceReportResponse>(`/policies/${id}/compliance-report/`),
  sendReminder: (id: number) => client.post<{ detail: string; count: number }>(`/policies/${id}/send-reminder/`, {}),
  pendingAcknowledgements: () => client.get<PolicyItem[]>("/policies/pending-acknowledgements/"),
};
