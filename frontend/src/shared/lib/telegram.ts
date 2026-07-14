// Определение режима работы (SPEC §2): браузер vs Telegram Mini App.
// Различается только слой авторизации; витрина/запись — общий код.

export function getTelegramWebApp() {
  return window.Telegram?.WebApp;
}

export function isMiniApp(): boolean {
  const tg = getTelegramWebApp();
  return Boolean(tg?.initData && tg.initData.length > 0);
}

// Вызывать один раз при старте в режиме Mini App.
export function initMiniApp(): void {
  const tg = getTelegramWebApp();
  if (!tg) return;
  tg.ready();
  tg.expand();
}
