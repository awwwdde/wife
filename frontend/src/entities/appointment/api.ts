import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/shared/api/client";
import type { Appointment, AppointmentCreate, Slot } from "./types";

export function useSlots(date: string, serviceIds: number[]) {
  return useQuery({
    queryKey: ["slots", date, serviceIds],
    enabled: Boolean(date) && serviceIds.length > 0,
    queryFn: async (): Promise<Slot[]> => {
      const { data } = await api.get<Slot[]>("/slots", {
        params: { date, service_ids: serviceIds },
        // FastAPI ждёт повторяющиеся ключи: service_ids=1&service_ids=2
        paramsSerializer: { indexes: null },
      });
      return data;
    },
  });
}

export function useCreateAppointment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: AppointmentCreate): Promise<Appointment> => {
      const { data } = await api.post<Appointment>("/appointments", payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-appointments"] }),
  });
}

export function useMyAppointments(enabled: boolean) {
  return useQuery({
    queryKey: ["my-appointments"],
    enabled,
    queryFn: async (): Promise<Appointment[]> => {
      const { data } = await api.get<Appointment[]>("/appointments/my");
      return data;
    },
  });
}

export function useCancelAppointment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number): Promise<Appointment> => {
      const { data } = await api.post<Appointment>(`/appointments/${id}/cancel`);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-appointments"] }),
  });
}
