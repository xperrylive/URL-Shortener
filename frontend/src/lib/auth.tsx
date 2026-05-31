"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { authAPI, type User } from "./api";

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    loading: true,
  });

  // Rehydrate from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userJson = localStorage.getItem("user");
    if (token && userJson) {
      try {
        setState({ user: JSON.parse(userJson), token, loading: false });
      } catch {
        setState({ user: null, token: null, loading: false });
      }
    } else {
      setState((s) => ({ ...s, loading: false }));
    }
  }, []);

  const persist = useCallback((user: User, token: string) => {
    localStorage.setItem("access_token", token);
    localStorage.setItem("user", JSON.stringify(user));
    setState({ user, token, loading: false });
  }, []);

  const clear = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setState({ user: null, token: null, loading: false });
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await authAPI.login(email, password);
      persist(res.user, res.access_token);
    },
    [persist],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const res = await authAPI.register(email, password);
      persist(res.user, res.access_token);
    },
    [persist],
  );

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (_) {}
    clear();
  }, [clear]);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        isAuthenticated: !!state.token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
