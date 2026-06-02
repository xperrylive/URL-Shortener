/**
 * API client — thin wrapper over fetch that:
 * - Always sends to NEXT_PUBLIC_API_URL (defaults to http://localhost:8000)
 * - Injects Authorization header from localStorage
 * - Throws APIError on non-2xx responses
 */

const BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

export class APIError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "APIError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const resp = await fetch(`${BASE_URL}${path}`, {
    credentials: "include", // send httpOnly refresh cookie
    ...options,
    headers,
  });

  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`;
    try {
      const body = await resp.json();
      detail = body.detail ?? detail;
    } catch (_) {}
    throw new APIError(resp.status, detail);
  }

  // 204 No Content
  if (resp.status === 204) return undefined as T;

  return resp.json() as Promise<T>;
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  tier: "free" | "pro";
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export const authAPI = {
  register: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  refresh: () =>
    request<TokenResponse>("/api/auth/refresh", { method: "POST" }),

  logout: () =>
    request<void>("/api/auth/logout", { method: "DELETE" }),
};

// ── URLs ──────────────────────────────────────────────────────────────────────

export interface ShortURL {
  id: string;
  original_url: string;
  short_code: string;
  short_url: string;
  custom_alias: string | null;
  user_id: string | null;
  is_active: boolean;
  expires_at: string | null;
  click_count: number;
  created_at: string;
  updated_at: string;
}

export interface URLListResponse {
  items: ShortURL[];
  total: number;
  total_active: number;
  total_clicks: number;
  page: number;
  page_size: number;
  pages: number;
}

export const urlsAPI = {
  shorten: (url: string, custom_alias?: string, expires_at?: string) =>
    request<ShortURL>("/api/urls/shorten", {
      method: "POST",
      body: JSON.stringify({ url, custom_alias, expires_at }),
    }),

  list: (page = 1, page_size = 10) =>
    request<URLListResponse>(`/api/urls/?page=${page}&page_size=${page_size}`),

  get: (short_code: string) =>
    request<ShortURL>(`/api/urls/${short_code}`),

  delete: (short_code: string) =>
    request<void>(`/api/urls/${short_code}`, { method: "DELETE" }),

  update: (short_code: string, data: Partial<Pick<ShortURL, "is_active" | "expires_at" | "custom_alias">>) =>
    request<ShortURL>(`/api/urls/${short_code}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};
