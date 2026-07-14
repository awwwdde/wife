import { useMemo, useState } from "react";
import { useServices } from "@/entities/service/api";
import { useCreateAppointment, useSlots } from "@/entities/appointment/api";
import type { Slot } from "@/entities/appointment/types";
import { useAuth } from "@/shared/auth/AuthProvider";
import { TelegramLoginWidget } from "@/features/auth/TelegramLoginWidget";

// Поток записи. БЕЗ стилей — стандартные элементы; дизайн определим позже.
function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

function fmtTime(iso: string): string {
  return new Date(iso).toLocaleString("ru-RU", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function BookingWizard() {
  const { me, isMiniApp } = useAuth();
  const { data: services } = useServices();
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [date, setDate] = useState<string>(todayISO());
  const [slot, setSlot] = useState<Slot | null>(null);
  const [comment, setComment] = useState("");
  const [consent, setConsent] = useState(false);

  const slotsQuery = useSlots(date, selectedIds);
  const createMut = useCreateAppointment();

  const total = useMemo(() => {
    const chosen = (services ?? []).filter((s) => selectedIds.includes(s.id));
    const minutes = chosen.reduce((a, s) => a + s.duration_min, 0);
    const price = chosen.reduce((a, s) => a + Number(s.price), 0);
    return { minutes, price };
  }, [services, selectedIds]);

  const toggle = (id: number) => {
    setSlot(null);
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const canSubmit = Boolean(me) && Boolean(slot) && consent && !createMut.isPending;

  const submit = () => {
    if (!slot) return;
    createMut.mutate({
      service_ids: selectedIds,
      start_at: slot.start_at,
      comment: comment || undefined,
      consent,
      source: isMiniApp ? "miniapp" : "site",
    });
  };

  if (createMut.isSuccess) {
    return (
      <div>
        <h2>Запись создана</h2>
        <p>
          {createMut.data.services.map((s) => s.title).join(", ")} —{" "}
          {new Date(createMut.data.start_at).toLocaleString("ru-RU")}
        </p>
        <p>Точный адрес студии придёт после подтверждения.</p>
        <a href="/cabinet">Мои записи</a>
      </div>
    );
  }

  return (
    <div>
      {/* Шаг 1: услуги */}
      <fieldset>
        <legend>1. Услуги</legend>
        {(services ?? []).map((s) => (
          <label key={s.id} style={{ display: "block" }}>
            <input
              type="checkbox"
              checked={selectedIds.includes(s.id)}
              onChange={() => toggle(s.id)}
            />
            {s.title} — {s.price} ₽, {s.duration_min} мин
          </label>
        ))}
        {selectedIds.length > 0 && (
          <p>
            Итого: {total.minutes} мин, {total.price} ₽
          </p>
        )}
      </fieldset>

      {/* Шаг 2: дата и слот */}
      <fieldset disabled={selectedIds.length === 0}>
        <legend>2. Дата и время</legend>
        <input
          type="date"
          value={date}
          min={todayISO()}
          onChange={(e) => {
            setDate(e.target.value);
            setSlot(null);
          }}
        />
        <div>
          {slotsQuery.isLoading && <span>Загрузка слотов…</span>}
          {slotsQuery.data && slotsQuery.data.length === 0 && (
            <span>На эту дату свободных слотов нет.</span>
          )}
          {slotsQuery.data?.map((s) => (
            <button
              key={s.start_at}
              type="button"
              onClick={() => setSlot(s)}
              aria-pressed={slot?.start_at === s.start_at}
            >
              {fmtTime(s.start_at)}
              {slot?.start_at === s.start_at ? " ✓" : ""}
            </button>
          ))}
        </div>
      </fieldset>

      {/* Шаг 3: авторизация */}
      <fieldset disabled={!slot}>
        <legend>3. Авторизация</legend>
        {me ? (
          <p>
            Вы вошли как {me.first_name ?? me.username ?? `id ${me.telegram_id}`}.
          </p>
        ) : isMiniApp ? (
          <p>Авторизация через Telegram…</p>
        ) : (
          <TelegramLoginWidget />
        )}
      </fieldset>

      {/* Шаг 4: согласие и подтверждение */}
      <fieldset disabled={!me || !slot}>
        <legend>4. Подтверждение</legend>
        <label style={{ display: "block" }}>
          Комментарий (необязательно):
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
        </label>
        <label style={{ display: "block" }}>
          <input
            type="checkbox"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
          />
          Согласен на обработку персональных данных (
          <a href="/privacy" target="_blank" rel="noreferrer">
            политика
          </a>
          )
        </label>
        <button type="button" onClick={submit} disabled={!canSubmit}>
          {createMut.isPending ? "Создаём…" : "Записаться"}
        </button>
        {createMut.isError && (
          <p role="alert">
            {(createMut.error as { response?: { status?: number } })?.response?.status ===
            409
              ? "Этот слот уже занят — выберите другое время."
              : "Не удалось создать запись. Попробуйте ещё раз."}
          </p>
        )}
      </fieldset>
    </div>
  );
}
