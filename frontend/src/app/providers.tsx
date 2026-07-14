import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { AuthProvider } from "@/shared/auth/AuthProvider";
import { SmoothScroll } from "@/shared/lib/lenis";
import { initMiniApp, isMiniApp } from "@/shared/lib/telegram";

export function AppProviders({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient());

  useEffect(() => {
    if (isMiniApp()) initMiniApp();
  }, []);

  return (
    <QueryClientProvider client={client}>
      <AuthProvider>
        <SmoothScroll>{children}</SmoothScroll>
      </AuthProvider>
    </QueryClientProvider>
  );
}
