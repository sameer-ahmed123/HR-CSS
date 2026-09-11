export type UserRole = "ADMIN" | "HR" | "TEAM_LEAD" | "EMPLOYEE" | "FINANCE";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  phone_number: string;
  is_active: boolean;
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
