// ============================================================
// src/contexts/AuthContext.tsx
// Global auth state — single source of truth.
// ============================================================
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { auth, authApi, type UserProfile } from '@/lib/api';

interface AuthContextValue {
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (token: string) => Promise<UserProfile>;
  logout: () => void;
  refresh: () => Promise<UserProfile | null>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(() => auth.getUser());
  const [isLoading, setIsLoading] = useState<boolean>(() => Boolean(auth.getToken()));

  const refresh = useCallback(async (): Promise<UserProfile | null> => {
    const token = auth.getToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return null;
    }

    try {
      const profile = await authApi.me();
      auth.save(token, profile);
      setUser(profile);
      return profile;
    } catch {
      auth.clear();
      setUser(null);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Verify token on mount
  useEffect(() => {
    if (auth.getToken()) {
      void refresh();
    } else {
      setIsLoading(false);
    }
  }, [refresh]);

  const login = useCallback(async (token: string): Promise<UserProfile> => {
    localStorage.setItem('access_token', token);
    const profile = await authApi.me();
    auth.save(token, profile);
    setUser(profile);
    return profile;
  }, []);

  const logout = useCallback(() => {
    auth.clear();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: Boolean(user),
      login,
      logout,
      refresh,
    }),
    [user, isLoading, login, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used inside <AuthProvider>');
  }
  return ctx;
}