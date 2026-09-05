import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, clearToken, getToken, Me, setToken } from "../api/client";

interface AuthContextValue {
  isAuthenticated: boolean;
  me: Me | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = async () => {
    if (!getToken()) {
      setMe(null);
      return;
    }
    try {
      const profile = await api.getMe();
      setMe(profile);
    } catch {
      clearToken();
      setMe(null);
    }
  };

  useEffect(() => {
    refreshMe().finally(() => setLoading(false));
  }, []);

  const login = async (token: string) => {
    setToken(token);
    await refreshMe();
  };

  const logout = () => {
    clearToken();
    setMe(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated: !!me, me, loading, login, logout, refreshMe }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
