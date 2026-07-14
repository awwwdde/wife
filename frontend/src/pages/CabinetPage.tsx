import { Link } from "react-router-dom";
import { useCancelAppointment, useMyAppointments } from "@/entities/appointment/api";
import { useAuth } from "@/shared/auth/AuthProvider";

const STATUS_RU: Record<string, string> = {
  pending: "ожидает",
  confirmed: "подтверждена",
  completed: "завершена",
  cancelled: "отменена",
  no_show: "не пришёл",
};

export function CabinetPage() {
  const { me, loading } = useAuth();
  const list = useMyAppointments(Boolean(me));
  const cancelMut = useCancelAppointment();

  if (loading) return <main><p>Загрузка…</p></main>;

  if (!me) {
    return (
      <main>
        <p>
          <Link to="/">← На главную</Link>
        </p>
        <h1>Мои записи</h1>
        <p>
          Войдите, чтобы увидеть записи. Откройте раздел <Link to="/booking">записи</Link>{" "}
          или Mini App внутри Telegram.
        </p>
      </main>
    );
  }

  return (
    <main>
      <p>
        <Link to="/">← На главную</Link>
      </p>
      <h1>Мои записи</h1>
      {list.isLoading && <p>Загрузка записей…</p>}
      {list.data && list.data.length === 0 && <p>Записей пока нет.</p>}
      <ul>
        {list.data?.map((a) => (
          <li key={a.id}>
            {new Date(a.start_at).toLocaleString("ru-RU")} —{" "}
            {a.services.map((s) => s.title).join(", ")} [{STATUS_RU[a.status] ?? a.status}]
            {(a.status === "pending" || a.status === "confirmed") && (
              <button
                type="button"
                onClick={() => cancelMut.mutate(a.id)}
                disabled={cancelMut.isPending}
              >
                Отменить
              </button>
            )}
          </li>
        ))}
      </ul>
      {cancelMut.isError && (
        <p role="alert">
          Отмена возможна не позднее чем за 6 часов до визита.
        </p>
      )}
    </main>
  );
}
