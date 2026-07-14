import { useServices } from "@/entities/service/api";

// Витрина услуг — тянет из БД (backend GET /api/services).
export function Services() {
  const { data, isLoading, isError } = useServices();

  return (
    <section id="services" className="px-6 md:px-16 py-24">
      <h2 className="font-serif text-4xl md:text-5xl mb-12">Услуги</h2>

      {isLoading && <p className="opacity-60">Загрузка услуг…</p>}
      {isError && (
        <p className="opacity-60">
          Не удалось загрузить услуги. Проверь, что backend запущен и применён сид.
        </p>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {data?.map((s) => (
          <article
            key={s.id}
            className="border border-graphite/15 rounded-2xl p-6 hover:border-terracotta transition-colors"
          >
            <div className="flex items-baseline justify-between gap-4">
              <h3 className="font-serif text-2xl">{s.title}</h3>
              <span className="text-terracotta whitespace-nowrap">{s.price} ₽</span>
            </div>
            {s.description && <p className="mt-3 opacity-70">{s.description}</p>}
            <p className="mt-4 text-sm opacity-50">{s.duration_min} мин</p>
          </article>
        ))}
      </div>
    </section>
  );
}
