import client from "./client";

export interface DocumentTypeOption {
  id: number;
  code: string;
  name: string;
  description?: string | null;
  turnaround_days?: number;
  is_active?: boolean;
}

export interface DocumentRequestItem {
  id: number;
  requested_by?: number;
  requested_by_email?: string;
  document_type: number;
  document_type_name: string;
  purpose: string;
  needed_by: string;
  expected_completion_date?: string | null;
  status: string;
  rejection_reason?: string | null;
  assigned_hr?: number | null;
  assigned_hr_email?: string | null;
  generated_file?: string | null;
  reference_number?: string | null;
  file_version?: number;
  manual_upload?: boolean;
  created_at: string;
  updated_at: string;
}

export const documentApi = {
  listDocumentTypes: () => client.get<DocumentTypeOption[]>("/documents/types/"),
  listMyRequests: () => client.get<DocumentRequestItem[]>("/documents/request/"),
  createRequest: (payload: { document_type: number; purpose: string; needed_by: string }) =>
    client.post<DocumentRequestItem>("/documents/request/", payload),
  updateRequest: (id: number, payload: Record<string, unknown>) =>
    client.patch<DocumentRequestItem>(`/documents/request/${id}/`, payload),
  getRequest: (id: number) => client.get<DocumentRequestItem>(`/documents/request/${id}/`),
};
