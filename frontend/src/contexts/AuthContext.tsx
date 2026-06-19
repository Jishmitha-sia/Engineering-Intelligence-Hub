"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api";
import {
  AuthResponse,
  User,
  clearStoredToken,
  getStoredToken,
  setStoredToken,
} from "@/lib/auth";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    fullName?: string,
  ) => Promise<void>;
  applyAuthResponse: (response: AuthResponse) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const storedToken = getStoredToken();
    if (!storedToken) {
      setUser(null);
      setToken(null);
      return;
    }

    const profile = await apiRequest<User>(
      "/api/v1/auth/me",
      { method: "GET" },
      storedToken,
    );
    setUser(profile);
    setToken(storedToken);
  }, []);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        await refreshUser();
      } catch {
        clearStoredToken();
        setUser(null);
        setToken(null);
      } finally {
        setIsLoading(false);
      }
    };

    void bootstrap();
  }, [refreshUser]);

  const applyAuthResponse = useCallback((response: AuthResponse) => {
    setStoredToken(response.data.access_token);
    setToken(response.data.access_token);
    setUser(response.data.user);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await apiRequest<AuthResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      applyAuthResponse(response);
      router.push("/dashboard");
    },
    [applyAuthResponse, router],
  );

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      const response = await apiRequest<AuthResponse>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          full_name: fullName || null,
        }),
      });

      applyAuthResponse(response);
      router.push("/dashboard");
    },
    [applyAuthResponse, router],
  );

  const logout = useCallback(async () => {
    if (token) {
      try {
        await apiRequest(
          "/api/v1/auth/logout",
          { method: "POST" },
          token,
        );
      } catch {
        // Logout is client-side for JWT; ignore API errors.
      }
    }

    clearStoredToken();
    setUser(null);
    setToken(null);
    router.push("/login");
  }, [router, token]);

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      login,
      register,
      applyAuthResponse,
      logout,
      refreshUser,
    }),
    [user, token, isLoading, login, register, applyAuthResponse, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
