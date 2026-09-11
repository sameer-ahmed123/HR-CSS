import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

const client = axios.create({ baseURL: "/api/v1", headers: { "Content-Type": "application/json" } });

client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshRequest: Promise<string> | null = null;

client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (error.response?.status !== 401 || !original || original._retry || original.url?.includes("/auth/token")) {
      return Promise.reject(error);
    }
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) return Promise.reject(error);
    original._retry = true;
    try {
      refreshRequest ??= axios.post<{ access: string }>("/api/v1/auth/token/refresh/", { refresh }).then(({ data }) => data.access);
      const access = await refreshRequest;
      refreshRequest = null;
      localStorage.setItem("access_token", access);
      original.headers.Authorization = `Bearer ${access}`;
      return client(original);
    } catch (refreshError) {
      refreshRequest = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      return Promise.reject(refreshError);
    }
  },
);

export default client;
