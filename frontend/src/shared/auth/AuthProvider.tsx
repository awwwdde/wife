import { createContext, useContext, useEffect, useState } from "react";
import {
  authMiniApp,
  authWidget,
  fetchMe,
  logout as apiLogout,
  type Me,
  type WidgetPayload,
} from "@/entities/auth/api";
import { getTelegramWebApp, isMiniApp } from "@/shared/lib/telegram";

interface AuthState {
  me: Me | null;
  loading: boolean;
  isMiniApp: boolean;
  loginWithWidget: (payload: WidgetPayload) => Promise<void>;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);
  const miniApp = isMiniApp();

  useEffect(() => {
    (async () => {
      try {
        if (miniApp) {
          // Mini App: авторизуемся автоматически по initData.
          const initData = getTelegramWebApp()?.initData ?? "";
          setMe(await authMiniApp(initData));
        } else {
          // Браузер: пробуем восстановить сессию по cookie.
          setMe(await fetchMe());
        }
      } catch {
        setMe(null);
      } finally {
        setLoading(false);
      }
    })();
  }, [miniApp]);

  const loginWithWidget = async (payload: WidgetPayload) => {
    setMe(await authWidget(payload));
  };

  const refresh = async () => {
    try {
      setMe(await fetchMe());
    } catch {
      setMe(null);
    }
  };

  const logout = async () => {
    await apiLogout();
    setMe(null);
  };

  return (
    <AuthContext.Provider
      value={{ me, loading, isMiniApp: miniApp, loginWithWidget, refresh, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
