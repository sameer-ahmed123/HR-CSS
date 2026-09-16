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
