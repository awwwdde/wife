import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createManualAppointment,
  listAppointments,
  listServices,
  setAppointmentStatus,
} from "@/entities/admin/api";

const STATUSES = ["confirmed", "completed", "cancelled", "no_show"];
const todayISO = () => new Date().toISOString().slice(0, 10);

export function AppointmentsAdmin() {
  const qc = useQueryClient();
  const [day, setDay] = useState(todayISO());
  const from = new Date(`${day}T00:00`).toISOString();
  const to = new Date(new Date(`${day}T00:00`).getTime() + 86400000).toISOString();

  const { data } = useQuery({
    queryKey: ["admin-appointments", day],
    queryFn: () => listAppointments(from, to),
  });
  const appts = Array.isArray(data) ? data : [];

  const { data: servicesData } = useQuery({ queryKey: ["admin-services"], queryFn: listServices });
  const services = (Array.isArray(servicesData) ? servicesData : []).filter((s) => s.is_active);

  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      setAppointmentStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-appointments"] }),
  });

  // Ручная запись
  const [ids, setIds] = useState<number[]>([]);
  const [when, setWhen] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const createMut = useMutation({
    mutationFn: () =>
      createManualAppointment({
        service_ids: ids,
        start_at: new Date(when).toISOString(),
        new_client: { first_name: name, phone: phone || undefined },
      }),
    onSuccess: () => {
      setIds([]); setWhen(""); setName(""); setPhone("");
      qc.invalidateQueries({ queryKey: ["admin-appointments"] });
    },
  });

  return (
    <section>
      <h2>Записи</h2>
      <label>День:{" "}
        <input type="date" value={day} onChange={(e) => setDay(e.target.value)} />
      </label>
      <table>
        <thead>
          <tr><th>Время</th><th>Клиент</th><th>Услуги</th><th>Статус</th><th>Исход</th></tr>
        </thead>
        <tbody>
          {appts.map((a) => (
            <tr key={a.id}>
              <td>{new Date(a.start_at).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })}</td>
              <td>{a.client_name ?? "—"}{a.client_phone ? ` (${a.client_phone})` : ""}</td>
              <td>{a.services.join(", ")}</td>
              <td>{a.status}</td>
              <td>
                {STATUSES.map((st) => (
                  <button
                    key={st}
                    onClick={() => statusMut.mutate({ id: a.id, status: st })}
                    disabled={statusMut.isPending || a.status === st}
                  >
                    {st}
                  </button>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {appts.length === 0 && <p>Записей на этот день нет.</p>}

      <h3>Ручная запись</h3>
      <div>
        {services.map((s) => (
          <label key={s.id} style={{ display: "block" }}>
            <input
              type="checkbox"
              checked={ids.includes(s.id)}
              onChange={() =>
                setIds((p) => (p.includes(s.id) ? p.filter((x) => x !== s.id) : [...p, s.id]))
              }
            />
            {s.title} ({s.duration_min} мин)
          </label>
        ))}
      </div>
      <p>
        <input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
      </p>
      <p>
        <input placeholder="Имя клиента" value={name} onChange={(e) => setName(e.target.value)} />
        <input placeholder="Телефон" value={phone} onChange={(e) => setPhone(e.target.value)} />
      </p>
      <button
        onClick={() => createMut.mutate()}
        disabled={createMut.isPending || ids.length === 0 || !when || !name}
      >
        Создать запись
      </button>
      {createMut.isError && (
        <p role="alert">
          {(createMut.error as { response?: { status?: number } })?.response?.status === 409
            ? "Слот занят — выберите другое время."
            : "Не удалось создать запись."}
        </p>
      )}
    </section>
  );
}
