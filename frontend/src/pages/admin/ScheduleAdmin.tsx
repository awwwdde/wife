import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { getSchedule, putSchedule, type WorkingHoursItem } from "@/entities/admin/api";

const DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

// "HH:MM:SS" | null → "HH:MM" для input type=time
const toInput = (t: string | null) => (t ? t.slice(0, 5) : "");
const fromInput = (v: string) => (v ? `${v}:00` : null);

export function ScheduleAdmin() {
  const { data } = useQuery({ queryKey: ["admin-schedule"], queryFn: getSchedule });
  const [rows, setRows] = useState<WorkingHoursItem[]>([]);

  useEffect(() => {
    // Гарантируем 7 дней (0..6), даже если в БД чего-то нет.
    const byDay = new Map((data ?? []).map((w) => [w.weekday, w]));
    setRows(
      Array.from({ length: 7 }, (_, wd) =>
        byDay.get(wd) ?? { weekday: wd, start_time: null, end_time: null, is_day_off: true },
      ),
    );
  }, [data]);

  const save = useMutation({ mutationFn: () => putSchedule(rows) });

  const patch = (wd: number, p: Partial<WorkingHoursItem>) =>
    setRows((prev) => prev.map((r) => (r.weekday === wd ? { ...r, ...p } : r)));

  return (
    <section>
      <h2>График работы</h2>
      <table>
        <thead>
          <tr><th>День</th><th>Начало</th><th>Конец</th><th>Выходной</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.weekday}>
              <td>{DAYS[r.weekday]}</td>
              <td>
                <input
                  type="time"
                  value={toInput(r.start_time)}
                  disabled={r.is_day_off}
                  onChange={(e) => patch(r.weekday, { start_time: fromInput(e.target.value) })}
                />
              </td>
              <td>
                <input
                  type="time"
                  value={toInput(r.end_time)}
                  disabled={r.is_day_off}
                  onChange={(e) => patch(r.weekday, { end_time: fromInput(e.target.value) })}
                />
              </td>
              <td>
                <input
                  type="checkbox"
                  checked={r.is_day_off}
                  onChange={(e) => patch(r.weekday, { is_day_off: e.target.checked })}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button onClick={() => save.mutate()} disabled={save.isPending}>
        {save.isPending ? "Сохранение…" : "Сохранить график"}
      </button>
      {save.isSuccess && <span> Сохранено ✓</span>}
    </section>
  );
}
