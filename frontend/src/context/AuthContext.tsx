import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import client from "../api/client";
import type {
  LoginCredentials,
  RegisterCredentials,
  TokenResponse,
  User,
} from "../types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
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
    client
      .get<User>("/auth/me/")
      .then(({ data }) => setUser(data))
      .catch(() => logout())
      .finally(() => setLoading(false));
  }, [token]);

  async function login(credentials: LoginCredentials) {
    const { data } = await client.post<TokenResponse>(
      "/auth/token/",
      credentials,
    );
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    setToken(data.access);
    const profile = await client.get<User>("/auth/me/");
    setUser(profile.data);
  }

  async function register(credentials: RegisterCredentials) {
    await client.post<User>("/auth/register/", credentials);
    await login({ email: credentials.email, password: credentials.password });
  }

  function logout() {
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
        logout,
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
