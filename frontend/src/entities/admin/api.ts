import { api } from "@/shared/api/client";

// --- Типы (зеркалят admin-схемы бэка) ---
export interface AdminMe {
  email: string;
}

export interface ServiceAdmin {
  id: number;
  title: string;
  description: string | null;
  duration_min: number;
  buffer_min: number;
  price: string;
  deposit_amount: string | null;
  category: string | null;
  photo_url: string | null;
  is_active: boolean;
}

export interface WorkingHoursItem {
  weekday: number;
  start_time: string | null; // "HH:MM:SS"
  end_time: string | null;
  is_day_off: boolean;
}

export interface MasterSettings {
  id: number;
  name: string;
  phone: string | null;
  timezone: string;
  address: string | null;
  slot_step_min: number;
  cancellation_hours: number;
}

export interface ClientListItem {
  id: number;
  first_name: string | null;
  last_name: string | null;
  username: string | null;
  phone: string | null;
  telegram_id: number | null;
}

export interface AppointmentAdmin {
  id: number;
  start_at: string;
  end_at: string;
  status: string;
  source: string;
  comment: string | null;
  client_id: number;
  client_name: string | null;
  client_phone: string | null;
  services: string[];
}

// --- Auth ---
export const adminLogin = (email: string, password: string, totp_code: string) =>
  api.post<AdminMe>("/admin/login", { email, password, totp_code }).then((r) => r.data);
export const adminMe = () => api.get<AdminMe>("/admin/me").then((r) => r.data);
export const adminLogout = () => api.post("/admin/logout").then((r) => r.data);

// --- Services ---
export const listServices = () =>
  api.get<ServiceAdmin[]>("/admin/services").then((r) => r.data);
export const createService = (body: Partial<ServiceAdmin>) =>
  api.post<ServiceAdmin>("/admin/services", body).then((r) => r.data);
export const updateService = (id: number, body: Partial<ServiceAdmin>) =>
  api.patch<ServiceAdmin>(`/admin/services/${id}`, body).then((r) => r.data);
export const deleteService = (id: number) =>
  api.delete(`/admin/services/${id}`).then((r) => r.data);

// --- Schedule ---
export const getSchedule = () =>
  api.get<WorkingHoursItem[]>("/admin/schedule").then((r) => r.data);
export const putSchedule = (items: WorkingHoursItem[]) =>
  api.put<WorkingHoursItem[]>("/admin/schedule", items).then((r) => r.data);

// --- Settings ---
export const getSettings = () =>
  api.get<MasterSettings>("/admin/settings").then((r) => r.data);
export const updateSettings = (body: Partial<MasterSettings>) =>
  api.patch<MasterSettings>("/admin/settings", body).then((r) => r.data);

// --- Clients ---
export const listClients = (q?: string) =>
  api.get<ClientListItem[]>("/admin/clients", { params: q ? { q } : {} }).then((r) => r.data);

// --- Appointments ---
export const listAppointments = (from: string, to: string) =>
  api
    .get<AppointmentAdmin[]>("/admin/appointments", {
      params: { from, to },
      paramsSerializer: { indexes: null },
    })
    .then((r) => r.data);
export const setAppointmentStatus = (id: number, status: string) =>
  api.patch<AppointmentAdmin>(`/admin/appointments/${id}/status`, { status }).then((r) => r.data);
export const createManualAppointment = (body: {
  service_ids: number[];
  start_at: string;
  comment?: string;
  client_id?: number;
  new_client?: { first_name: string; phone?: string };
}) => api.post<AppointmentAdmin>("/admin/appointments", body).then((r) => r.data);
