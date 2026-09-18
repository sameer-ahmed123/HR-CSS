export type UserRole = "ADMIN" | "HR" | "TEAM_LEAD" | "EMPLOYEE" | "FINANCE";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  phone_number: string;
  department?: number | null;
  department_name?: string | null;
  is_active: boolean;
  created_at?: string;
}

export interface TokenResponse { access: string; refresh: string; }
export interface LoginCredentials { email: string; password: string; }
export interface RegisterCredentials {
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  password: string;
  password_confirmation: string;
}
export interface LoginResponse extends TokenResponse { user: User; }
export interface Department { id: number; name: string; code: string; description: string; head: number | null; }
export interface InviteCredentials { email: string; first_name: string; last_name: string; role: UserRole; department: number; }
export interface InviteVerification { email: string; first_name: string; expires_at: string; }
export interface LoginHistory { id: number; ip_address: string | null; user_agent: string; status: "SUCCESS" | "FAILED"; timestamp: string; }
export interface SentInvite { user_id: number; email: string; role: UserRole; is_active: boolean; status: "Pending" | "Activated"; created_at: string; }
export interface LockedUser { id: number; email: string; first_name: string; last_name: string; role: UserRole; failed_login_attempts: number; locked_at: string | null; }
export interface OrganizationUser { id: number; email: string; first_name: string; last_name: string; role: UserRole; department_name: string | null; is_active: boolean; created_at: string; }
export type HiringRequestUrgency = "LOW" | "MEDIUM" | "HIGH" | "URGENT";
export type HiringRequestStatus = "DRAFT" | "PENDING" | "APPROVED" | "REJECTED" | "MORE_INFO";
export type JobStatus = "DRAFT" | "PUBLISHED" | "CLOSED";
export type ApplicationStage = "NEW" | "REVIEWED" | "SHORTLISTED" | "TEST_SENT" | "INTERVIEW" | "OFFER" | "HIRED" | "REJECTED";

export interface HiringRequestInput {
  request_title: string;
  department: number;
  headcount: number;
  seniority: string;
  budget: string | null;
  reason: string;
  urgency: HiringRequestUrgency;
  required_experience: string;
  required_qualifications: string;
}

export interface HiringRequest extends HiringRequestInput {
  id: number;
  requested_by: number;
  seniority: string;
  budget: string | null;
  reason: string;
  required_experience: string;
  required_qualifications: string;
  status: HiringRequestStatus;
  rejection_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface RecruitmentOpenJob {
  id: number;
  job_title: string;
  department_name: string;
  status: JobStatus;
  cv_score_threshold: number;
  applicant_count: number;
  created_at: string;
}

export interface RecruitmentPendingRequest {
  id: number;
  request_title: string;
  department_name: string;
  requested_by_name: string;
  headcount: number;
  urgency: HiringRequestUrgency;
  status: HiringRequestStatus;
  created_at: string;
}

export interface PriorityApplication {
  id: number;
  candidate_name: string;
  candidate_email: string;
  job_title: string;
  stage: ApplicationStage;
  ats_score: number;
  is_priority: boolean;
  created_at: string;
}

export interface RecruitmentOverview {
  total_open_jobs: number;
  pending_hiring_requests_count: number;
  new_applications_this_week: number;
  emails_sent_this_week: number;
  open_jobs: RecruitmentOpenJob[];
  pending_hiring_requests: RecruitmentPendingRequest[];
  priority_candidates: PriorityApplication[];
  pipeline_funnel: Partial<Record<ApplicationStage, number>>;
}
