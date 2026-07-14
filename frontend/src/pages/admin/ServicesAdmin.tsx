import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createService,
  deleteService,
  listServices,
  updateService,
  type ServiceAdmin,
} from "@/entities/admin/api";

// CRUD услуг. Без стилей — стандартные элементы.
function ServiceRow({ s }: { s: ServiceAdmin }) {
  const qc = useQueryClient();
  const [title, setTitle] = useState(s.title);
  const [price, setPrice] = useState(s.price);
  const [duration, setDuration] = useState(String(s.duration_min));
  const [buffer, setBuffer] = useState(String(s.buffer_min));
  const [active, setActive] = useState(s.is_active);

  const save = useMutation({
    mutationFn: () =>
      updateService(s.id, {
        title,
        price,
        duration_min: Number(duration),
        buffer_min: Number(buffer),
        is_active: active,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-services"] }),
  });
  const del = useMutation({
    mutationFn: () => deleteService(s.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-services"] }),
  });

  return (
    <tr>
      <td>{s.id}</td>
      <td><input value={title} onChange={(e) => setTitle(e.target.value)} /></td>
      <td><input value={price} onChange={(e) => setPrice(e.target.value)} size={6} /></td>
      <td><input value={duration} onChange={(e) => setDuration(e.target.value)} size={4} /></td>
      <td><input value={buffer} onChange={(e) => setBuffer(e.target.value)} size={4} /></td>
      <td>
        <input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)} />
      </td>
      <td>
        <button onClick={() => save.mutate()} disabled={save.isPending}>Сохранить</button>
        <button onClick={() => del.mutate()} disabled={del.isPending}>Удалить</button>
      </td>
    </tr>
  );
}

export function ServicesAdmin() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["admin-services"], queryFn: listServices });
  const services = Array.isArray(data) ? data : [];

  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [duration, setDuration] = useState("60");
  const create = useMutation({
    mutationFn: () =>
      createService({
        title,
        price,
        duration_min: Number(duration),
      }),
    onSuccess: () => {
      setTitle("");
      setPrice("");
      qc.invalidateQueries({ queryKey: ["admin-services"] });
    },
  });

  return (
    <section>
      <h2>Услуги</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Название</th><th>Цена</th><th>Мин</th><th>Буфер</th><th>Активна</th><th></th>
          </tr>
        </thead>
        <tbody>
          {services.map((s) => <ServiceRow key={s.id} s={s} />)}
        </tbody>
      </table>

      <h3>Добавить услугу</h3>
      <input placeholder="Название" value={title} onChange={(e) => setTitle(e.target.value)} />
      <input placeholder="Цена" value={price} onChange={(e) => setPrice(e.target.value)} size={6} />
      <input placeholder="Минут" value={duration} onChange={(e) => setDuration(e.target.value)} size={4} />
      <button onClick={() => create.mutate()} disabled={create.isPending || !title || !price}>
        Добавить
      </button>
    </section>
  );
}
