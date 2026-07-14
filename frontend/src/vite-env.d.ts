/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_BOT_USERNAME?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Telegram WebApp SDK (подключён скриптом в index.html).
interface Window {
  Telegram?: {
    WebApp?: {
      initData: string;
      initDataUnsafe: Record<string, unknown>;
      expand: () => void;
      ready: () => void;
      themeParams: Record<string, string>;
      requestContact?: (cb: (ok: boolean) => void) => void;
      MainButton: unknown;
    };
  };
}
