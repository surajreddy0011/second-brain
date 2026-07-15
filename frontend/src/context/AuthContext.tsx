import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import * as api from "../api";

interface AuthContextValue {
  user: api.User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("token"));
  const [user, setUser] = useState<api.User | null>(null);
  const [loading, setLoading] = useState(true);

  // Runs once when the app loads. If a token was saved from a previous
  // visit, verify it's still valid and restore the logged-in state —
  // this is what keeps you logged in after refreshing the page.
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api.getMe(token)
      .then(setUser)
      .catch(() => {
        setToken(null);
        localStorage.removeItem("token");
      })
      .finally(() => setLoading(false));
  }, [token]);

  async function login(email: string, password: string) {
    const { access_token } = await api.login(email, password);
    localStorage.setItem("token", access_token);
    setToken(access_token);
    setUser(await api.getMe(access_token));
  }

  async function signup(email: string, password: string) {
    await api.signup(email, password);
    await login(email, password);
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}