import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { authApi } from "../api/auth";
import type {
  LoginCredentials,
  LoginResponse,
  RegisterCredentials,
  User,
} from "../types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  acceptInvite: (token: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  setSession: (response: LoginResponse) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem("access_token"),
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    async function loadUser() {
      try {
        const { data } = await authApi.me();
        setUser(data);
      } catch {
        await logout();
      } finally {
        setLoading(false);
      }
    }
    void loadUser();
  }, [token]);

  async function login(credentials: LoginCredentials) {
    const { data } = await authApi.login(credentials);
    setSession(data);
  }

  function setSession(data: LoginResponse) {
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    setToken(data.access);
    setUser(data.user);
  }

  async function register(credentials: RegisterCredentials) {
    await authApi.register(credentials);
    await login({ email: credentials.email, password: credentials.password });
  }

  async function acceptInvite(inviteToken: string, password: string) {
    const { data } = await authApi.acceptInvite(inviteToken, password);
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    setToken(data.access);
    setUser(data.user);
  }

  async function logout() {
    const refresh = localStorage.getItem("refresh_token");
    if (refresh) {
      try {
        await authApi.logout(refresh);
      } catch {}
    }
    clearSession();
  }

  async function logoutAll() {
    try {
      await authApi.logoutAll();
    } catch {}
    clearSession();
  }

  function clearSession() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    setToken(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: Boolean(user && token),
        login,
        register,
        acceptInvite,
        logout,
        logoutAll,
        setSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
