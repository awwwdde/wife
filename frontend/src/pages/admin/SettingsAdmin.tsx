import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { getSettings, updateSettings } from "@/entities/admin/api";

export function SettingsAdmin() {
  const { data } = useQuery({ queryKey: ["admin-settings"], queryFn: getSettings });
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [slot, setSlot] = useState("30");
  const [cancel, setCancel] = useState("6");

  useEffect(() => {
    if (data) {
      setName(data.name);
      setAddress(data.address ?? "");
      setSlot(String(data.slot_step_min));
      setCancel(String(data.cancellation_hours));
    }
  }, [data]);

  const save = useMutation({
    mutationFn: () =>
      updateSettings({
        name,
        address,
        slot_step_min: Number(slot),
        cancellation_hours: Number(cancel),
      }),
  });

  return (
    <section>
      <h2>Настройки</h2>
      <p>
        <label>Имя мастера:{" "}
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
      </p>
      <p>
        <label>Приватный адрес (клиенту — после записи):<br />
          <textarea value={address} onChange={(e) => setAddress(e.target.value)} cols={40} />
        </label>
      </p>
      <p>
        <label>Шаг слота (мин):{" "}
          <input value={slot} onChange={(e) => setSlot(e.target.value)} size={4} />
        </label>
      </p>
      <p>
        <label>Отмена не позднее (часов):{" "}
          <input value={cancel} onChange={(e) => setCancel(e.target.value)} size={4} />
        </label>
      </p>
      <button onClick={() => save.mutate()} disabled={save.isPending}>Сохранить</button>
      {save.isSuccess && <span> Сохранено ✓</span>}
    </section>
  );
}
