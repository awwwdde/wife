// CRM (админка) — ленивый чанк на секретном роуте /admin110220 (DECISIONS §2).
// Вход логин+пароль+2FA, календарь, база клиентов, услуги, аналитика — Фаза 4.
export default function AdminApp() {
  return (
    <main className="min-h-screen px-6 md:px-16 py-16">
      <h1 className="font-serif text-4xl mb-4">askbrows · CRM</h1>
      <p className="opacity-70">
        Каркас админки. Вход (логин+пароль+2FA) и модули (календарь, клиенты, услуги,
        график, рассылки, аналитика) — Фаза 4.
      </p>
    </main>
  );
}
