import { useEffect, useRef } from "react";
import type { WidgetPayload } from "@/entities/auth/api";
import { useAuth } from "@/shared/auth/AuthProvider";

// Браузерный вход через официальный Telegram Login Widget.
// ВНИМАНИЕ: работает только на домене, привязанном к боту в BotFather (/setdomain).
// На localhost Telegram виджет не покажет — это ожидаемо (см. DECISIONS, риски Фазы 2).
export function TelegramLoginWidget() {
  const ref = useRef<HTMLDivElement>(null);
  const { loginWithWidget } = useAuth();
  const botUsername = import.meta.env.VITE_BOT_USERNAME;

  useEffect(() => {
    // Telegram вызывает глобальный колбэк с данными пользователя.
    (window as unknown as Record<string, unknown>).onTelegramAuth = (
      user: WidgetPayload,
    ) => {
      void loginWithWidget(user);
    };

    if (!botUsername || !ref.current) return;
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;
    script.setAttribute("data-telegram-login", botUsername);
    script.setAttribute("data-size", "large");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    script.setAttribute("data-request-access", "write");
    ref.current.appendChild(script);
  }, [botUsername, loginWithWidget]);

  if (!botUsername) {
    return <p>VITE_BOT_USERNAME не задан — вход через виджет недоступен.</p>;
  }

  return (
    <div>
      <div ref={ref} />
      <p>
        <small>
          Виджет Telegram работает только на привязанном к боту домене. На localhost
          он не отобразится — используйте вход через Mini App внутри Telegram.
        </small>
      </p>
    </div>
  );
}
