export interface Slot {
  start_at: string; // UTC ISO
}

export interface ServiceBrief {
  id: number;
  title: string;
  duration_min: number;
  price: string;
}

export type AppointmentStatus =
  | "pending"
  | "confirmed"
  | "completed"
  | "cancelled"
  | "no_show";

export interface Appointment {
  id: number;
  start_at: string;
  end_at: string;
  status: AppointmentStatus;
  comment: string | null;
  services: ServiceBrief[];
}

export interface AppointmentCreate {
  service_ids: number[];
  start_at: string;
  comment?: string;
  consent: boolean;
  source?: "site" | "miniapp";
}
