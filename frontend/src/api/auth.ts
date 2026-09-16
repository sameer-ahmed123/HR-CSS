import client from "./client";
import type { InviteCredentials, InviteVerification, LockedUser, LoginCredentials, LoginHistory, LoginResponse, OrganizationUser, RegisterCredentials, SentInvite, User } from "../types";

export const authApi = {
  login: (credentials: LoginCredentials) => client.post<LoginResponse>("/auth/login/", credentials),
  me: () => client.get<User>("/auth/me/"),
  logout: (refresh: string) => client.post<void>("/auth/logout/", { refresh }),
  logoutAll: () => client.post<void>("/auth/logout-all/"),
  register: (credentials: RegisterCredentials) => client.post<User>("/auth/register/", credentials),
  verifyInvite: (token: string) => client.get<InviteVerification>("/auth/invites/verify/", { params: { token } }),
  acceptInvite: (token: string, password: string) => client.post<LoginResponse>("/auth/invites/accept/", { token, password }),
  createInvite: (credentials: InviteCredentials) => client.post<User>("/auth/invites/", credentials),
  listOrganizationUsers: () => client.get<OrganizationUser[]>("/auth/users/"),
  listLockedUsers: () => client.get<LockedUser[]>("/auth/users/locked/"),
  unlockUser: (userId: number) => client.post<{ detail: string }>(`/auth/users/${userId}/unlock/`),
  resendInvite: (userId: number) => client.post<void>(`/auth/invites/${userId}/resend/`),
  requestPasswordReset: (email: string) => client.post<{ detail: string }>("/auth/password-reset/request/", { email }),
  verifyPasswordReset: (token: string) => client.get<{ valid: boolean }>("/auth/password-reset/verify/", { params: { token } }),
  confirmPasswordReset: (token: string, password: string, passwordConfirmation: string) => client.post<LoginResponse>("/auth/password-reset/confirm/", { token, password, password_confirmation: passwordConfirmation }),
  changePassword: (oldPassword: string, newPassword: string, confirmation: string) => client.post<void>("/auth/password-change/", { old_password: oldPassword, new_password: newPassword, new_password_confirmation: confirmation }),
  loginHistory: () => client.get<LoginHistory[]>("/auth/login-history/"),
  myInvites: () => client.get<SentInvite[]>("/auth/my-invites/"),
};