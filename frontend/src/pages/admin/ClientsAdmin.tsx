import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listClients } from "@/entities/admin/api";

export function ClientsAdmin() {
  const [q, setQ] = useState("");
  const { data } = useQuery({
    queryKey: ["admin-clients", q],
    queryFn: () => listClients(q || undefined),
  });
  const clients = Array.isArray(data) ? data : [];

  return (
    <section>
      <h2>Клиенты</h2>
      <input placeholder="Поиск (имя/телефон)" value={q} onChange={(e) => setQ(e.target.value)} />
      <table>
        <thead>
          <tr><th>ID</th><th>Имя</th><th>Телефон</th><th>Telegram</th></tr>
        </thead>
        <tbody>
          {clients.map((c) => (
            <tr key={c.id}>
              <td>{c.id}</td>
              <td>{[c.first_name, c.last_name].filter(Boolean).join(" ") || "—"}</td>
              <td>{c.phone ?? "—"}</td>
              <td>{c.username ? `@${c.username}` : (c.telegram_id ?? "—")}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {clients.length === 0 && <p>Клиентов не найдено.</p>}
    </section>
  );
}
