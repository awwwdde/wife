import { useEffect, useState } from "react";
import { adminLogin, adminLogout, adminMe, type AdminMe } from "@/entities/admin/api";
import { AppointmentsAdmin } from "./AppointmentsAdmin";
import { ClientsAdmin } from "./ClientsAdmin";
import { ScheduleAdmin } from "./ScheduleAdmin";
import { ServicesAdmin } from "./ServicesAdmin";
import { SettingsAdmin } from "./SettingsAdmin";

// CRM (админка). Без стилей — дизайн определим позже. Секретный роут /admin110220.
type Tab = "appointments" | "services" | "schedule" | "clients" | "settings";

function LoginForm({ onOk }: { onOk: (me: AdminMe) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setBusy(true);
    setError("");
    try {
      onOk(await adminLogin(email, password, code));
    } catch {
      setError("Неверные данные или код 2FA.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main>
      <h1>askbrows · CRM</h1>
      <p><input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} /></p>
      <p>
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </p>
      <p>
        <input
          placeholder="Код 2FA (6 цифр)"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
      </p>
      <button onClick={submit} disabled={busy || !email || !password || !code}>
        {busy ? "Вход…" : "Войти"}
      </button>
      {error && <p role="alert">{error}</p>}
    </main>
  );
}

export default function AdminApp() {
  const [me, setMe] = useState<AdminMe | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("appointments");

  useEffect(() => {
    adminMe()
      .then(setMe)
      .catch(() => setMe(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <main><p>Загрузка…</p></main>;
  if (!me) return <LoginForm onOk={setMe} />;

  const logout = async () => {
    await adminLogout();
    setMe(null);
  };

  return (
    <main>
      <h1>askbrows · CRM</h1>
      <p>
        {me.email} · <button onClick={logout}>Выйти</button>
      </p>
      <nav>
        <button onClick={() => setTab("appointments")}>Записи</button>{" "}
        <button onClick={() => setTab("services")}>Услуги</button>{" "}
        <button onClick={() => setTab("schedule")}>График</button>{" "}
        <button onClick={() => setTab("clients")}>Клиенты</button>{" "}
        <button onClick={() => setTab("settings")}>Настройки</button>
      </nav>
      <hr />
      {tab === "appointments" && <AppointmentsAdmin />}
      {tab === "services" && <ServicesAdmin />}
      {tab === "schedule" && <ScheduleAdmin />}
      {tab === "clients" && <ClientsAdmin />}
      {tab === "settings" && <SettingsAdmin />}
    </main>
  );
}
