// Заглушки секций визитки (наполнение — фаза 1/2: контент из БД + портфолио).
// Адрес студии приватный — на публичном сайте НЕ показываем (DECISIONS §3).

export function Portfolio() {
  return (
    <section id="portfolio" className="px-6 md:px-16 py-24 bg-graphite/[0.03]">
      <h2 className="font-serif text-4xl md:text-5xl mb-6">Портфолио</h2>
      <p className="opacity-60">Галерея «до/после» — добавит мастер через CRM.</p>
    </section>
  );
}

export function About() {
  return (
    <section id="about" className="px-6 md:px-16 py-24">
      <h2 className="font-serif text-4xl md:text-5xl mb-6">Обо мне</h2>
      <p className="max-w-2xl opacity-70">
        Черновик-заглушка: привет, меня зовут Ангелина. Делаю брови и ресницы так,
        чтобы подчёркивать естественную красоту. Текст мастер отредактирует позже.
      </p>
    </section>
  );
}

export function Reviews() {
  return (
    <section id="reviews" className="px-6 md:px-16 py-24 bg-graphite/[0.03]">
      <h2 className="font-serif text-4xl md:text-5xl mb-6">Отзывы</h2>
      <p className="opacity-60">
        Отзывы собираются через бота после визита и публикуются после модерации.
      </p>
    </section>
  );
}

export function Contacts() {
  return (
    <section id="contacts" className="px-6 md:px-16 py-24">
      <h2 className="font-serif text-4xl md:text-5xl mb-6">Контакты</h2>
      <p className="opacity-70">
        Запись — онлайн через сайт или Telegram. Точный адрес студии отправим после
        подтверждения записи.
      </p>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="px-6 md:px-16 py-10 text-sm opacity-50">
      © {new Date().getFullYear()} askbrows · Москва
    </footer>
  );
}
